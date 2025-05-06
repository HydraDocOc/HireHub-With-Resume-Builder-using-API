import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from flask_cors import CORS
from flask_migrate import Migrate

# Configure logging
logging.basicConfig(level=logging.DEBUG)


# Initialize Flask and SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization","X-CSRFToken", "X-Requested-With"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type"]
    }
})


# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///jobs.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.String(500))
    jobs = db.relationship('Job', backref='company', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    job_type = db.Column(db.String(50))
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    requirements = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# -------------------------
#        API ROUTES
# -------------------------
@app.after_request
def after_request(response):
    return response

@app.route('/api/jobs', methods=['GET'])
def api_get_jobs():
    try:
        # Get query parameters for search
        keyword = request.args.get('keyword', '')
        location = request.args.get('location', '')
        
        # Build query
        query = Job.query
        
        # Apply filters if provided
        if keyword:
            query = query.filter(
                db.or_(
                    Job.title.ilike(f'%{keyword}%'),
                    Job.description.ilike(f'%{keyword}%')
                )
            )
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        # Order by posted date
        jobs = query.order_by(Job.posted_date.desc()).all()
        
        return jsonify([{
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "company": job.company.name,
            "company_id": job.company.id,
            "company_logo_url": job.company.logo_url,
            "location": job.location,
            "salary_range": job.salary_range,
            "job_type": job.job_type,
            "posted_date": job.posted_date.isoformat(),
            "requirements": job.requirements
        } for job in jobs])
    except Exception as e:
        logging.error(f"Error in api_get_jobs: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/job/<int:job_id>', methods=['GET'])
def api_get_job_detail(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        return jsonify({
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "company": job.company.name,
            "company_id": job.company.id,
            "company_logo_url": job.company.logo_url,
            "location": job.location,
            "salary_range": job.salary_range,
            "job_type": job.job_type,
            "posted_date": job.posted_date.isoformat(),
            "requirements": job.requirements
        })
    except Exception as e:
        logging.error(f"Error in api_get_job_detail: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/job', methods=['POST'])
def api_post_job():
    try:
        data = request.get_json()
        print("📥 Received POST at /api/job")
        print("Incoming data:", data)

        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        company_id = data.get('company_id')
        company = Company.query.get(company_id)

        if not company:
            return jsonify({"error": f"Company with ID {company_id} not found"}), 404

        job = Job(
            title=data.get('title'),
            description=data.get('description'),
            company=company,
            location=data.get('location'),
            salary_range=data.get('salary_range'),
            job_type=data.get('job_type'),
            requirements=data.get('requirements')
        )

        db.session.add(job)
        db.session.commit()

        print("✅ Job added:", job.id)
        return jsonify({"message": "Job posted successfully", "job_id": job.id}), 201

    except KeyError as e:
        logging.error(f"Missing required field: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"Error in api_post_job: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/api/job/<int:job_id>', methods=['OPTIONS', 'PUT'])
def api_update_job(job_id):
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'Preflight accepted'})
        response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:8000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'PUT')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    try:
        
        # Debug logging
        app.logger.info(f"Received PUT request for job {job_id}")
        app.logger.info(f"Headers: {request.headers}")
        app.logger.info(f"Remote IP: {request.remote_addr}")

        # Verify content type
        if not request.is_json:
            app.logger.error("Request must be JSON")
            return jsonify({"error": "Request must be JSON"}), 400

        # Get and validate data
        data = request.get_json()
        if not data:
            app.logger.error("No data provided")
            return jsonify({"error": "No data provided"}), 400

        # Get the job to update
        job = Job.query.get(job_id)
        if not job:
            app.logger.error(f"Job {job_id} not found")
            return jsonify({"error": f"Job {job_id} not found"}), 404

        # Update fields
        update_fields = [
            'title', 'description', 'location',
            'salary_range', 'job_type', 'requirements', 'company_id'
        ]

        for field in update_fields:
            if field in data:
                # Special handling for company_id
                if field == 'company_id':
                    company = Company.query.get(data['company_id'])
                    if not company:
                        app.logger.error(f"Company {data['company_id']} not found")
                        return jsonify({"error": f"Company {data['company_id']} not found"}), 404
                    setattr(job, field, data[field])
                else:
                    setattr(job, field, data[field])

        # Commit changes
        db.session.commit()
        app.logger.info(f"Successfully updated job {job_id}")
        return jsonify({
            "message": "Job updated successfully",
            "job_id": job_id,
            "updated_fields": [f for f in update_fields if f in data]
        })

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating job {job_id}: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to update job",
            "details": str(e)
        }), 500

@app.route('/api/job/<int:job_id>', methods=['DELETE'])
def api_delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return jsonify({"message": "Job deleted successfully"})
    except Exception as e:
        logging.error(f"Error in api_delete_job: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/companies', methods=['GET'])
def api_list_companies():
    try:
        companies = Company.query.all()
        return jsonify([{
            "id": company.id,
            "name": company.name,
            "description": company.description,
            "logo_url": company.logo_url
        } for company in companies])
    except Exception as e:
        logging.error(f"Error in api_list_companies: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/company/<int:company_id>', methods=['GET'])
def api_get_company(company_id):
    try:
        company = Company.query.get_or_404(company_id)
        return jsonify({
            "id": company.id,
            "name": company.name,
            "description": company.description,
            "logo_url": company.logo_url,
            "jobs": [{
                "id": job.id,
                "title": job.title,
                "location": job.location,
                "job_type": job.job_type,
                "posted_date": job.posted_date.isoformat()
            } for job in company.jobs]
        })
    except Exception as e:
        logging.error(f"Error in api_get_company: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/company', methods=['POST'])
def api_create_company():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'message': 'Preflight accepted'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    try:
        data = request.get_json()
        
        # Validate logo URL
        logo_url = data.get('logo_url', '')
        if not logo_url.startswith(('http://', 'https://')):
            logo_url = ''  # Set empty if invalid
        
        company = Company(
            name=data['name'],
            description=data.get('description', ''),
            logo_url=logo_url
        )
        
        db.session.add(company)
        db.session.commit()
        
        return jsonify({
            "message": "Company created successfully",
            "company": {
                "id": company.id,
                "name": company.name,
                "logo_url": company.logo_url,
                "description": company.description
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# -------------------------
# AUTH ROUTES
# -------------------------

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already registered"}), 400
            
        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email'],
            mobile=data['mobile'],
            role=data.get('role', 'user')
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"})
    except KeyError as e:
        logging.error(f"Missing required field: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"Error in api_register: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check credentials
        user = User.query.filter_by(email=data['email'], role=data.get('role', 'user')).first()
        if user and user.check_password(data['password']):
            login_user(user)
            return jsonify({
                "message": "Login successful", 
                "user_id": user.id,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            })
        return jsonify({"error": "Invalid credentials"}), 401
    except KeyError as e:
        logging.error(f"Missing required field: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"Error in api_login: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

# -------------------------
# ERROR HANDLERS
# -------------------------

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"error": "Access Forbidden"}), 403

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource Not Found"}), 404

@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal Server Error"}), 500

# -------------------------
# DB INITIALIZATION
# -------------------------

with app.app_context():
    db.create_all()
    
    # Only create admin user if doesn't exist
    if not User.query.filter_by(role="admin").first():
        admin_user = User(
            name="Admin",
            email="admin@example.com",
            mobile="1234567890",
            role="admin"
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()

# -------------------------
# APP ENTRY POINT
# -------------------------

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
