from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL(app)
@app.route('/')
def home():
    return render_template('index.html')


# Helper functions
def fetch_all(query, params=None):
    cur = mysql.connection.cursor()
    cur.execute(query, params or ())
    data = cur.fetchall()
    cur.close()
    return data

def execute_query(query, params):
    cur = mysql.connection.cursor()
    cur.execute(query, params)
    mysql.connection.commit()
    cur.close()


# Routes for Users
@app.route('/users')
def users():
    data = fetch_all("SELECT * FROM Users")
    return render_template('users.html', users=data)

@app.route('/add_user', methods=['POST'])
def add_user():
    user_id, name, email, password, role = (
        request.form['user_id'],
        request.form['name'],
        request.form['email'],
        request.form['password'],
        request.form['role']
    )
    execute_query(
        "INSERT INTO Users (user_id, name, email, password, role) VALUES (%s, %s, %s, %s, %s)",
        (user_id, name, email, password, role),
    )
    flash("User Added Successfully!")
    return redirect(url_for('users'))

@app.route('/search_users', methods=['GET'])
def search_users():
    search_query = request.args.get('query', '')  # Get the search query from the URL
    if search_query:
        query = "SELECT * FROM Users WHERE name LIKE %s OR email LIKE %s"
        data = fetch_all(query, (f"%{search_query}%", f"%{search_query}%"))
    else:
        data = fetch_all("SELECT * FROM Users")
    return render_template('users.html', users=data)


@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if request.method == 'POST':
        # Get updated values from the form
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Update the user in the database
        execute_query(
            "UPDATE Users SET name = %s, email = %s, password = %s, role = %s WHERE user_id = %s",
            (name, email, password, role, user_id)
        )
        flash("User Updated Successfully!")
        return redirect(url_for('users'))

    # Fetch the existing user details for pre-filling the form
    user = fetch_all("SELECT * FROM Users WHERE user_id = %s", (user_id,))
    if not user:
        flash("User not found!")
        return redirect(url_for('users'))

    return render_template('update_user.html', user=user[0])


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    execute_query("DELETE FROM Users WHERE user_id = %s", [user_id])
    flash("User Deleted Successfully!")
    return redirect(url_for('users'))

# Routes for Hackathons
@app.route('/hackathons')
def hackathons():
    data = fetch_all("SELECT * FROM Hackathons")
    return render_template('hackathons.html', hackathons=data)

@app.route('/add_hackathon', methods=['POST'])
def add_hackathon():
    try:
        hackathon_id = request.form['hackathon_id']
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        status = request.form['status']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Hackathons (hackathon_id, title, description, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (hackathon_id, title, description, start_date, end_date, status))
        mysql.connection.commit()
        cur.close()
        flash('Hackathon added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')  # Capture trigger error and display it
    return redirect(url_for('home'))



@app.route('/search_hackathons', methods=['GET'])
def search_hackathons():
    search_query = request.args.get('query', '')  # Get the search query from the URL
    if search_query:
        query = "SELECT * FROM Hackathons WHERE title LIKE %s OR description LIKE %s"
        data = fetch_all(query, (f"%{search_query}%", f"%{search_query}%"))
    else:
        data = fetch_all("SELECT * FROM Hackathons")
    return render_template('hackathons.html', hackathons=data)

@app.route('/update_hackathon/<int:hackathon_id>', methods=['GET', 'POST'])
def update_hackathon(hackathon_id):
    try:
        if request.method == 'GET':
            # Fetch the hackathon details to display in the form
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM Hackathons WHERE hackathon_id = %s", (hackathon_id,))
            hackathon = cur.fetchone()
            cur.close()
            if hackathon:
                return render_template('update_hackathon.html', hackathon=hackathon)
            else:
                flash('Hackathon not found.', 'error')
                return redirect(url_for('home'))

        if request.method == 'POST':
            # Handle form submission and update the hackathon
            title = request.form['title']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            status = request.form['status']

            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE Hackathons
                SET title = %s, description = %s, start_date = %s, end_date = %s, status = %s
                WHERE hackathon_id = %s
            """, (title, description, start_date, end_date, status, hackathon_id))
            mysql.connection.commit()
            cur.close()

            flash('Hackathon updated successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to the home page or hackathons list
    except Exception as e:
        flash(f'Error: {e}', 'error')  # Capture trigger error and display it
        return redirect(url_for('home'))


    # Fetch the existing hackathon details for pre-filling the form
    hackathon = fetch_all("SELECT * FROM Hackathons WHERE hackathon_id = %s", (hackathon_id,))
    if not hackathon:
        flash("Hackathon not found!")
        return redirect(url_for('hackathons'))

    return render_template('update_hackathon.html', hackathon=hackathon[0])


@app.route('/delete_hackathon/<int:hackathon_id>')
def delete_hackathon(hackathon_id):
    execute_query("DELETE FROM Hackathons WHERE hackathon_id = %s", [hackathon_id])
    flash("Hackathon Deleted Successfully!")
    return redirect(url_for('hackathons'))

# Routes for Teams
@app.route('/teams')
def teams():
    data = fetch_all("SELECT * FROM Teams")
    return render_template('teams.html', teams=data)

# Add Team Route
@app.route('/add_team', methods=['POST'])
def add_team():
    team_id = request.form['team_id']  # Primary key is entered manually
    team_name = request.form['team_name']
    hackathon_id = request.form['hackathon_id']
    member_id = request.form['member_id']
    is_leader = 1 if 'is_leader' in request.form else 0

    # Insert team into the database
    execute_query(
        "INSERT INTO Teams (team_id, team_name, hackathon_id, member_id, is_leader) VALUES (%s, %s, %s, %s, %s)",
        (team_id, team_name, hackathon_id, member_id, is_leader),
    )
    flash("Team Added Successfully!")
    return redirect(url_for('teams'))

@app.route('/search_teams', methods=['GET'])
def search_teams():
    search_query = request.args.get('query', '')  # Get the search query from the URL parameter
    if search_query:
        # Search for teams where the name matches the query (case-insensitive)
        query = "SELECT * FROM Teams WHERE team_name LIKE %s"
        data = fetch_all(query, (f"%{search_query}%",))
    else:
        # If no search query is provided, return all teams
        data = fetch_all("SELECT * FROM Teams")
    return {'teams': data}


# Update Team Route
@app.route('/update_team/<int:team_id>', methods=['GET', 'POST'])
def update_team(team_id):
    if request.method == 'POST':
        team_name = request.form['team_name']
        hackathon_id = request.form['hackathon_id']
        member_id = request.form['member_id']
        is_leader = 1 if 'is_leader' in request.form else 0

        # Update team in the database
        execute_query(
            "UPDATE Teams SET team_name = %s, hackathon_id = %s, member_id = %s, is_leader = %s WHERE team_id = %s",
            (team_name, hackathon_id, member_id, is_leader, team_id),
        )
        flash("Team Updated Successfully!")
        return redirect(url_for('teams'))

    # Fetch existing team details for pre-filling the form
    team = fetch_all("SELECT * FROM Teams WHERE team_id = %s", (team_id,))
    if not team:
        flash("Team not found!")
        return redirect(url_for('teams'))

    return render_template('update_team.html', team=team[0])

@app.route('/delete_team/<int:team_id>')
def delete_team(team_id):
    execute_query("DELETE FROM Teams WHERE team_id = %s", [team_id])
    flash("Team Deleted Successfully!")
    return redirect(url_for('teams'))

# Add similar routes for Projects, Judges, and Results...
# Routes for Projects
@app.route('/projects')
def projects():
    data = fetch_all("SELECT * FROM Projects")
    return render_template('projects.html', projects=data)

@app.route('/add_project', methods=['POST'])
def add_project():
    project_id, team_id, hackathon_id, project_title, description, project_link, submission_date, status = (
        request.form['project_id'],
        request.form['team_id'],
        request.form['hackathon_id'],
        request.form['project_title'],
        request.form['description'],
        request.form['project_link'],
        request.form['submission_date'],
        request.form['status']
    )
    execute_query(
        "INSERT INTO Projects (project_id, team_id, hackathon_id, project_title, description, project_link, submission_date, status) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (project_id, team_id, hackathon_id, project_title, description, project_link, submission_date, status),
    )
    flash("Project Added Successfully!")
    return redirect(url_for('projects'))

@app.route('/search_projects', methods=['GET'])
def search_projects():
    search_query = request.args.get('query', '')  # Get the search query from the URL
    if search_query:
        query = "SELECT * FROM Projects WHERE project_title LIKE %s OR description LIKE %s"
        data = fetch_all(query, (f"%{search_query}%", f"%{search_query}%"))
    else:
        data = fetch_all("SELECT * FROM Projects")
    return render_template('projects.html', projects=data)


@app.route('/update_project/<int:project_id>', methods=['GET', 'POST'])
def update_project(project_id):
    if request.method == 'POST':
        # Get updated values from the form
        team_id = request.form['team_id']
        hackathon_id = request.form['hackathon_id']
        project_title = request.form['project_title']
        description = request.form['description']
        project_link = request.form['project_link']
        submission_date = request.form['submission_date']
        status = request.form['status']

        # Update the project in the database
        execute_query(
            "UPDATE Projects SET team_id = %s, hackathon_id = %s, project_title = %s, description = %s, "
            "project_link = %s, submission_date = %s, status = %s WHERE project_id = %s",
            (team_id, hackathon_id, project_title, description, project_link, submission_date, status, project_id)
        )
        flash("Project Updated Successfully!")
        return redirect(url_for('projects'))

    # Fetch the existing project details for pre-filling the form
    project = fetch_all("SELECT * FROM Projects WHERE project_id = %s", (project_id,))
    if not project:
        flash("Project not found!")
        return redirect(url_for('projects'))

    return render_template('update_project.html', project=project[0])


@app.route('/delete_project/<int:project_id>')
def delete_project(project_id):
    execute_query("DELETE FROM Projects WHERE project_id = %s", [project_id])
    flash("Project Deleted Successfully!")
    return redirect(url_for('projects'))



# Routes for Judges
@app.route('/judges')
def judges():
    data = fetch_all("SELECT * FROM Judges")
    return render_template('judges.html', judges=data)

@app.route('/add_judge', methods=['POST'])
def add_judge():
    judge_id = request.form['judge_id']
    hackathon_id = request.form['hackathon_id']
    
    # Insert new judge into the database
    execute_query(
        "INSERT INTO Judges (judge_id, hackathon_id) VALUES (%s, %s)",
        (judge_id, hackathon_id)
    )
    flash("Judge Added Successfully!")
    return redirect(url_for('judges'))

@app.route('/search_judges', methods=['GET'])
def search_judges():
    search_query = request.args.get('query', '')  # Get the search query from the URL
    if search_query:
        query = "SELECT * FROM Judges WHERE judge_id LIKE %s OR hackathon_id LIKE %s"
        data = fetch_all(query, (f"%{search_query}%", f"%{search_query}%"))
    else:
        data = fetch_all("SELECT * FROM Judges")
    return render_template('judges.html', judges=data)


@app.route('/update_judge/<int:judge_id>/<int:hackathon_id>', methods=['GET', 'POST'])
def update_judge(judge_id, hackathon_id):
    if request.method == 'POST':
        # Get updated values from the form
        updated_judge_id = request.form['judge_id']
        updated_hackathon_id = request.form['hackathon_id']

        # Update the judge in the database
        execute_query(
            "UPDATE Judges SET judge_id = %s, hackathon_id = %s WHERE judge_id = %s AND hackathon_id = %s",
            (updated_judge_id, updated_hackathon_id, judge_id, hackathon_id)
        )
        flash("Judge Updated Successfully!")
        return redirect(url_for('judges'))

    # Fetch the existing judge details for pre-filling the form
    judge = fetch_all("SELECT * FROM Judges WHERE judge_id = %s AND hackathon_id = %s", (judge_id, hackathon_id))
    if not judge:
        flash("Judge not found!")
        return redirect(url_for('judges'))

    return render_template('update_judge.html', judge=judge[0])


@app.route('/delete_judge/<int:judge_id>/<int:hackathon_id>')
def delete_judge(judge_id, hackathon_id):
    execute_query("DELETE FROM Judges WHERE judge_id = %s AND hackathon_id = %s", (judge_id, hackathon_id))
    flash("Judge Deleted Successfully!")
    return redirect(url_for('judges'))


# Routes for Results
@app.route('/results')
def results():
    data = fetch_all("SELECT * FROM Results")
    return render_template('results.html', results=data)

@app.route('/add_result', methods=['POST'])
def add_result():
    result_id = request.form['result_id']
    hackathon_id = request.form['hackathon_id']
    team_id = request.form['team_id']
    position = request.form['position']

    execute_query(
        "INSERT INTO Results (result_id, hackathon_id, team_id, position) VALUES (%s, %s, %s, %s)",
        (result_id, hackathon_id, team_id, position)
    )
    flash("Result Added Successfully!")
    return redirect(url_for('results'))

@app.route('/search_results', methods=['GET'])
def search_results():
    search_query = request.args.get('query', '')  # Get the search query from the URL
    if search_query:
        query = "SELECT * FROM Results WHERE team_id LIKE %s OR position LIKE %s"
        data = fetch_all(query, (f"%{search_query}%", f"%{search_query}%"))
    else:
        data = fetch_all("SELECT * FROM Results")
    return render_template('results.html', results=data)


@app.route('/update_result/<int:result_id>', methods=['GET', 'POST'])
def update_result(result_id):
    if request.method == 'POST':
        hackathon_id = request.form['hackathon_id']
        team_id = request.form['team_id']
        position = request.form['position']

        execute_query(
            "UPDATE Results SET hackathon_id = %s, team_id = %s, position = %s WHERE result_id = %s",
            (hackathon_id, team_id, position, result_id)
        )
        flash("Result Updated Successfully!")
        return redirect(url_for('results'))

    result = fetch_all("SELECT * FROM Results WHERE result_id = %s", (result_id,))
    if not result:
        flash("Result not found!")
        return redirect(url_for('results'))

    return render_template('update_result.html', result=result[0])


@app.route('/delete_result/<int:result_id>')
def delete_result(result_id):
    execute_query("DELETE FROM Results WHERE result_id = %s", [result_id])
    flash("Result Deleted Successfully!")
    return redirect(url_for('results'))


if __name__ == '__main__':
    app.run(debug=True)
