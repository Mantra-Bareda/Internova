from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_migrate import Migrate
from databases import db, User, Task, InterviewSession, Resume, UserProfile
from gemini_service import generate_career_dashboard, generate_mock_interview_response, find_internships_for_user, generate_mock_interview_questions, generate_roadmap_chat_response, generate_career_alignment, generate_career_options, generate_specific_roadmap, generate_version_comparison
import os
import json
import PyPDF2
import docx
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///internova.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'default_internova_secret')

db.init_app(app)
migrate = Migrate(app, db, render_as_batch=True)

# Ensure tables are created
with app.app_context():
    db.create_all()

# Firebase Initialization
firebase_key_paths = [
    '/etc/secrets/firebase-auth.json',
    'firebase-auth.json',
    os.path.join(app.root_path, 'firebase-auth.json')
]

firebase_cred_path = next((path for path in firebase_key_paths if os.path.exists(path)), None)

if not firebase_cred_path:
    raise FileNotFoundError("firebase-auth.json not found in /etc/secrets/ or root directory.")

cred = credentials.Certificate(firebase_cred_path)
try:
    internova_firebase = firebase_admin.get_app('internova')
except ValueError:
    internova_firebase = firebase_admin.initialize_app(cred, name='internova')

@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    return render_template('index.html')

def extract_text_from_file(file):
    filename = file.filename.lower()
    text = ""
    try:
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            for para in doc.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    data = request.get_json(silent=True) or {}
    id_token = data.get('id_token')
    
    if not id_token:
        return jsonify({'error': 'No token provided'}), 400
        
    try:
        decoded_token = auth.verify_id_token(id_token, app=internova_firebase)
        email = decoded_token.get('email')
        
        if not email:
            return jsonify({'error': 'Email not found in token'}), 400
            
        user = User.query.filter_by(username=email).first()
        if not user:
            user = User(username=email, password="")
            db.session.add(user)
            db.session.commit()
            
        session['user_id'] = user.id
        return jsonify({'success': True, 'redirect': url_for('dashboard', user_id=user.id)})
        
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({'error': 'Authentication failed'}), 401

@app.route('/dashboard')
def dashboard_redirect():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard', user_id=session['user_id']))

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
            
        profile.first_name = request.form.get('first_name')
        profile.middle_name = request.form.get('middle_name')
        profile.last_name = request.form.get('last_name')
        profile.headline = request.form.get('headline')
        profile.bio = request.form.get('bio')
        profile.skills = request.form.get('skills')
        profile.education_details = request.form.get('education_details')
        profile.experience_details = request.form.get('experience_details')
        profile.linkedin_url = request.form.get('linkedin_url')
        profile.github_url = request.form.get('github_url')
        profile.portfolio_url = request.form.get('portfolio_url')
        
        db.session.commit()
        return render_template('account.html', profile=profile, success=True)
        
    return render_template('account.html', profile=profile)

@app.route('/dashboard/<int:user_id>')
def dashboard(user_id):
    if session.get('user_id') != user_id:
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    resumes = Resume.query.filter_by(user_id=user_id).order_by(Resume.created_at.desc()).all()
    
    resumes_data = []
    for r in resumes:
        score = "Processing..."
        if r.analysis_result:
            try:
                score = json.loads(r.analysis_result).get('skill_score', 'N/A')
            except json.JSONDecodeError:
                score = "Error"
        resumes_data.append({"id": r.id, "filename": r.filename, "score": score})
        
    return render_template('dashboard.html', user=user, resumes=resumes_data)

@app.route('/upload_version/<int:parent_resume_id>', methods=['POST'])
def upload_version(parent_resume_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    resume_file = request.files.get('resume_file')
    
    if resume_file and resume_file.filename:
        parent_resume = Resume.query.get_or_404(parent_resume_id)
        if parent_resume.user_id != user_id:
            return "Unauthorized", 401
            
        root_id = parent_resume.parent_resume_id if parent_resume.parent_resume_id else parent_resume.id
        max_version = db.session.query(db.func.max(Resume.version_number)).filter(
            (Resume.id == root_id) | (Resume.parent_resume_id == root_id)
        ).scalar() or 1
            
        resume_text = extract_text_from_file(resume_file)
        resume_file.close()
        
        new_resume = Resume(
            user_id=user_id, 
            filename=resume_file.filename, 
            resume_text=resume_text,
            parent_resume_id=root_id,
            version_number=max_version + 1
        )
        db.session.add(new_resume)
        db.session.commit()
        return redirect(url_for('view_resume', resume_id=new_resume.id))
        
    return redirect(url_for('view_resume', resume_id=parent_resume_id))

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    resume_file = request.files.get('resume_file')
    
    if resume_file and resume_file.filename:
        resume_text = extract_text_from_file(resume_file)
        
        # The file is processed in-memory and not saved to the server's disk.
        # We explicitly close the stream to clean up memory immediately.
        resume_file.close()
        
        new_resume = Resume(user_id=user_id, filename=resume_file.filename, resume_text=resume_text)
        db.session.add(new_resume)
        db.session.commit()
        return redirect(url_for('view_resume', resume_id=new_resume.id))
        
    return redirect(url_for('dashboard', user_id=user_id))

@app.route('/resume/<int:resume_id>')
def view_resume(resume_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return "Unauthorized", 401
        
    root_id = resume.parent_resume_id if resume.parent_resume_id else resume.id
    history = Resume.query.filter(
        (Resume.id == root_id) | (Resume.parent_resume_id == root_id)
    ).order_by(Resume.version_number.desc()).all()
    
    history_data = []
    for h in history:
        score = "N/A"
        if h.analysis_result:
            try:
                score = json.loads(h.analysis_result).get('skill_score', 'N/A')
            except:
                pass
        history_data.append({
            'id': h.id,
            'version': h.version_number,
            'score': score,
            'date': h.created_at.strftime('%b %d, %Y')
        })
        
    return render_template('resume.html', resume=resume, user=resume.user, history=history_data)

@app.route('/api/analyze_profile/<int:resume_id>', methods=['GET', 'POST'])
def analyze_profile(resume_id):
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user = User.query.get(session['user_id'])
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 401
    
    if resume.analysis_result:
        return jsonify(json.loads(resume.analysis_result))
        
    if user.credits < 1:
        return jsonify({"error": "Insufficient credits. Please contact the administrator."}), 403
        
    user.credits -= 1 # Deduct 1 credit for resume generation
    
    if resume.parent_resume_id:
        parent_resume = Resume.query.get(resume.parent_resume_id)
        if parent_resume and parent_resume.analysis_result:
            analysis = generate_version_comparison(parent_resume.resume_text, parent_resume.analysis_result, resume.resume_text)
            analysis['is_version_comparison'] = not analysis.get('is_good', False)
        else:
            analysis = generate_career_dashboard(resume.resume_text)
            analysis['is_version_comparison'] = False
    else:
        analysis = generate_career_dashboard(resume.resume_text)
        analysis['is_version_comparison'] = False
    
    resume.analysis_result = json.dumps(analysis)
    db.session.commit()
    
    return jsonify(analysis)

@app.route('/api/generate_advanced_content/<int:resume_id>', methods=['POST'])
def api_generate_advanced_content(resume_id):
    """API endpoint to generate internship, interview prep, roadmap options, and career alignment for 1 credit."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user = User.query.get(session['user_id'])
    resume = Resume.query.get_or_404(resume_id)
    
    if resume.user_id != user.id:
        return jsonify({"error": "Unauthorized"}), 401
        
    if user.credits < 1:
        return jsonify({"error": "Insufficient credits. Please contact the administrator."}), 403
        
    try:
        user.credits -= 1 # Deduct 1 credit for advanced bundle
        
        # 1. Internship Finder
        if not resume.internships_result:
            old_analysis_json = None
            if resume.parent_resume_id:
                parent_resume = Resume.query.get(resume.parent_resume_id)
                if parent_resume and parent_resume.analysis_result:
                    old_analysis_json = parent_resume.analysis_result
            resume.internships_result = json.dumps(find_internships_for_user(resume.resume_text, old_analysis_json))
            
        # 2. Interview Questions (generate multiple categories upfront)
        if not resume.interview_questions_result:
            resume.interview_questions_result = json.dumps({
                'general': generate_mock_interview_questions(resume.resume_text, 'general'),
                'technical': generate_mock_interview_questions(resume.resume_text, 'technical'),
                'behavioral': generate_mock_interview_questions(resume.resume_text, 'behavioral')
            })
            
        # 3. Career Alignment
        if not getattr(resume, 'career_alignment_result', None):
            resume.career_alignment_result = json.dumps(generate_career_alignment(resume.resume_text))
            
        # 4. AI Roadmap Options
        if not getattr(resume, 'roadmap_options_result', None):
            resume.roadmap_options_result = json.dumps(generate_career_options(resume.resume_text))
            
        db.session.commit()
        return jsonify({"success": True, "credits_remaining": user.credits})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete_resume/<int:resume_id>', methods=['DELETE'])
def api_delete_resume(resume_id):
    """API endpoint to delete a specific resume."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 401
        
    db.session.delete(resume)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    admin_email = os.environ.get('ADMIN_EMAIL')
    if not admin_email or user.username != admin_email:
        return "Unauthorized: You must be an admin to view this page.", 403
    users = User.query.all()
    return render_template('admin.html', users=users, current_user=user)

@app.route('/api/admin/update_credits', methods=['POST'])
def admin_update_credits():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    user = User.query.get(session['user_id'])
    admin_email = os.environ.get('ADMIN_EMAIL')
    if not admin_email or user.username != admin_email: return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json(silent=True) or {}
    target_user = User.query.get(data.get('user_id'))
    if target_user and data.get('credits') is not None:
        target_user.credits = int(data.get('credits'))
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Invalid user or data"}), 400

@app.route('/api/mock_interview', methods=['POST'])
def mock_interview():
    try:
        data = request.get_json(silent=True) or {}
        chat_history = data.get('history', '')
        message = data.get('message', '')
        
        reply = generate_mock_interview_response(chat_history, message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/internship_finder/<int:resume_id>')
def internship_finder(resume_id):
    """Page to display internship recommendations"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return "Unauthorized", 401
    return render_template('internship_finder.html', resume=resume, user=resume.user)

@app.route('/api/find_internships/<int:resume_id>', methods=['GET', 'POST'])
def api_find_internships(resume_id):
    """API endpoint to find internships based on resume"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    resume = Resume.query.get(resume_id)
    if not resume:
        return jsonify({"error": "Resume not found"}), 404
    if resume.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Check if we already have this data cached
    if resume.internships_result:
        try:
            return jsonify(json.loads(resume.internships_result))
        except json.JSONDecodeError:
            pass

    return jsonify({"error": "Data not generated yet. Please generate additional details from the Resume page.", "requires_generation": True}), 400

@app.route('/mock_interview_questions/<int:resume_id>')
def mock_interview_questions_page(resume_id):
    """Page for mock interview questions"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return "Unauthorized", 401
    return render_template('mock_interview_questions.html', resume=resume, user=resume.user)

@app.route('/api/generate_interview_questions/<int:resume_id>', methods=['GET', 'POST'])
def api_generate_interview_questions(resume_id):
    """API endpoint to generate mock interview questions"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 401
    
    role_type = request.args.get('type', 'general')
    
    # Check if we already have questions for this role type cached
    cached_questions = {}
    if resume.interview_questions_result:
        try:
            cached_questions = json.loads(resume.interview_questions_result)
            if role_type in cached_questions:
                return jsonify(cached_questions[role_type])
                
            # If user already spent 1 credit to unlock advanced content, allow them to generate other roles here on the fly
            questions_data = generate_mock_interview_questions(resume.resume_text, role_type)
            cached_questions[role_type] = questions_data
            resume.interview_questions_result = json.dumps(cached_questions)
            db.session.commit()
            return jsonify(questions_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Data not generated yet. Please generate additional details from the Resume page.", "requires_generation": True}), 400

@app.route('/virtual_office/<int:resume_id>')
def virtual_office(resume_id):
    """Coming soon page for Virtual Office"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return "Unauthorized", 401
    return render_template('virtual_office.html', resume=resume, user=resume.user)

@app.route('/in_app_internships/<int:resume_id>')
def in_app_internships(resume_id):
    """Coming soon page for In-App Partner Internships"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return "Unauthorized", 401
    return render_template('in_app_internships.html', resume=resume, user=resume.user)

@app.route('/roadmap/<int:resume_id>')
def roadmap_page(resume_id):
    """Page for Personalized AI Roadmap Chat"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return "Unauthorized", 401
    return render_template('roadmap.html', resume=resume, user=resume.user)

@app.route('/api/roadmap_chat/<int:resume_id>', methods=['POST'])
def api_roadmap_chat(resume_id):
    """API endpoint for roadmap chat"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json(silent=True) or {}
        chat_history = data.get('history', '')
        message = data.get('message', '')
        
        reply = generate_roadmap_chat_response(resume.resume_text, chat_history, message)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/career_alignment/<int:resume_id>')
def career_alignment_page(resume_id):
    """Page for AI-Powered Career Roadmap & Skill Alignment"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return "Unauthorized", 401
    return render_template('career_alignment.html', resume=resume, user=resume.user)

@app.route('/api/career_alignment/<int:resume_id>', methods=['POST'])
def api_career_alignment(resume_id):
    """API endpoint to get career alignment insights"""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']:
        return jsonify({"error": "Unauthorized"}), 401
        
    if getattr(resume, 'career_alignment_result', None):
        try: return jsonify(json.loads(resume.career_alignment_result))
        except json.JSONDecodeError: pass
        
    return jsonify({"error": "Data not generated yet. Please generate additional details from the Resume page.", "requires_generation": True}), 400

@app.route('/api/roadmap_options/<int:resume_id>', methods=['GET'])
def api_roadmap_options(resume_id):
    """API endpoint to get initial career path options"""
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']: return jsonify({"error": "Unauthorized"}), 401
    
    if getattr(resume, 'roadmap_options_result', None):
        try: return jsonify({"options": json.loads(resume.roadmap_options_result)})
        except json.JSONDecodeError: pass
        
    return jsonify({"error": "Data not generated yet. Please generate additional details from the Resume page.", "requires_generation": True}), 400

@app.route('/api/roadmap_generate/<int:resume_id>', methods=['POST'])
def api_roadmap_generate(resume_id):
    """API endpoint to generate the roadmap for a specific option"""
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != session['user_id']: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json(silent=True) or {}
    selected_option = data.get('option')
    
    try:
        roadmap_html = generate_specific_roadmap(resume.resume_text, selected_option)
        return jsonify({"roadmap": roadmap_html})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
