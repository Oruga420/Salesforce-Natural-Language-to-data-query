from flask import render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from models import User, db
from utils.openai_helper import interpret_query, generate_soql, format_response
from utils.salesforce_helper import authenticate_salesforce, execute_soql_query

def init_routes(app):
    @app.route('/')
    def home():
        if 'user_id' in session:
            return redirect(url_for('chat'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.id
                return redirect(url_for('chat'))
            return render_template('login.html', error="Invalid credentials")
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('login'))

    @app.route('/chat', methods=['GET', 'POST'])
    def chat():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        messages = user.messages

        if request.method == 'POST':
            user_query = request.form.get('query')
            if user_query:
                try:
                    # Interpret the user query
                    interpreted_query = interpret_query(user_query)
                    
                    # Generate SOQL query
                    soql_query = generate_soql(interpreted_query)
                    
                    # Execute SOQL query against Salesforce
                    sf_instance = authenticate_salesforce(user.salesforce_token, user.salesforce_instance_url)
                    result = execute_soql_query(sf_instance, soql_query)
                    
                    # Format the response
                    formatted_response = format_response(result)
                    
                    # Save messages to the database
                    user.add_message('user', user_query)
                    user.add_message('bot', formatted_response)
                    db.session.commit()
                    
                    messages = user.messages
                except Exception as e:
                    flash(str(e), 'error')

        return render_template('chat.html', messages=messages)

    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        
        user_query = request.form.get('query')
        if not user_query:
            return jsonify({"error": "No query provided"}), 400

        try:
            # Interpret the user query
            interpreted_query = interpret_query(user_query)
            
            # Generate SOQL query
            soql_query = generate_soql(interpreted_query)
            
            # Execute SOQL query against Salesforce
            user = User.query.get(session['user_id'])
            sf_instance = authenticate_salesforce(user.salesforce_token, user.salesforce_instance_url)
            result = execute_soql_query(sf_instance, soql_query)
            
            # Format the response
            formatted_response = format_response(result)
            
            # Save messages to the database
            user.add_message('user', user_query)
            user.add_message('bot', formatted_response)
            db.session.commit()
            
            return redirect(url_for('chat'))
        except Exception as e:
            return jsonify({"error": str(e)}), 500
