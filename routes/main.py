import os
import filetype
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.models import db, CV, Analysis, Feedback
from utils.analyzer import analyze_cv, extract_text_from_pdf, extract_text_from_docx

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/language/<lang>')
def set_language(lang):
    if lang in current_app.config['LANGUAGES']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('main.index'))

@main.route('/dashboard')
@login_required
def dashboard():
    cvs = CV.query.filter_by(user_id=current_user.id).order_by(CV.uploaded_at.desc()).all()
    return render_template('dashboard.html', cvs=cvs)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['cv_file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure upload folder exists
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(upload_path)
            
            # Deep file validation
            kind = filetype.guess(upload_path)
            ext = filename.rsplit('.', 1)[1].lower()
            
            # Allow docx explicitly since filetype sometimes struggles with it or flags it as zip
            if ext == 'pdf' and (not kind or kind.extension != 'pdf'):
                os.remove(upload_path)
                flash('Invalid file content. Expected a valid PDF.', 'danger')
                return redirect(request.url)
            elif ext == 'docx':
                # Basic check for docx (which is a zip file)
                if not kind or (kind.extension != 'docx' and kind.extension != 'zip'):
                    os.remove(upload_path)
                    flash('Invalid file content. Expected a valid DOCX.', 'danger')
                    return redirect(request.url)
            
            # Create CV record
            new_cv = CV(user_id=current_user.id, file_path=upload_path)
            db.session.add(new_cv)
            db.session.commit()
            
            # Perform Analysis
            ext = filename.rsplit('.', 1)[1].lower()
            text = ""
            if ext == 'pdf':
                text = extract_text_from_pdf(upload_path)
            elif ext == 'docx':
                text = extract_text_from_docx(upload_path)
                
            scores, overall, feedback_data = analyze_cv(text)
            
            new_analysis = Analysis(
                cv_id=new_cv.id,
                structure_score=scores['structure'],
                skills_score=scores['skills'],
                formatting_score=scores['formatting'],
                content_score=scores['content'],
                overall_score=overall
            )
            db.session.add(new_analysis)
            db.session.commit()
            
            import json
            new_feedback = Feedback(
                analysis_id=new_analysis.id,
                feedback_text=feedback_data['feedback_text'],
                suggestions=feedback_data['suggestions'],
                recommended_roles=json.dumps(feedback_data.get('recommended_roles', []))
            )
            db.session.add(new_feedback)
            db.session.commit()
            
            flash('CV uploaded and analyzed successfully!', 'success')
            return redirect(url_for('main.results', analysis_id=new_analysis.id))
            
        else:
            flash('Allowed file types are pdf, docx', 'danger')
            return redirect(request.url)
            
    return render_template('upload.html')

@main.route('/results/<int:analysis_id>')
@login_required
def results(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    # Ensure user owns this analysis
    if analysis.cv.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.dashboard'))
        
    feedback = Feedback.query.filter_by(analysis_id=analysis.id).first()
    
    import json
    recommended_roles = []
    if feedback and feedback.recommended_roles:
        try:
            recommended_roles = json.loads(feedback.recommended_roles)
        except:
            pass
            
    return render_template('results.html', analysis=analysis, feedback=feedback, recommended_roles=recommended_roles)
