from flask import redirect, render_template, url_for, request
import json
from flask_login import login_required, current_user, LoginManager
from sqlalchemy.exc import SQLAlchemyError
from .models import UnroastedCoffee, RoastedCoffee
from .data_analysis import get_top_five_sold, get_least_in_stock
from sqlalchemy.orm.exc import NoResultFound


from app import app, db

login_manager = LoginManager(app)
""""
HERE IS ALL THE VIEWS THAT REQUIRE THE APP THAT DONT REQUIRE AUTHORIZATION
like the log-in 
"""
from .auth import auth
app.register_blueprint(auth, url_prefix='/auth')


@app.route('/')
def index():
    #so when the app starts it automatically redirects you to the log in page
    return redirect(url_for('auth.login'))
    

@app.route('/roasted', methods=['GET', 'POST'])
@login_required
def roasted():
    roasted_coffee_list = get_roasted_coffee()

    success_message = request.args.get('success_message', None)
    error_message = request.args.get('error_message', None)


    return render_template("roasted.html", roasted_coffee_list=roasted_coffee_list, success_message=success_message, error_message=error_message)


@app.route('/unroasted', methods=['GET', 'POST'])
@login_required
def unroasted():
    #getting th coffee's so I can put it in the table
    unroasted_coffee_list = get_unroasted_coffee()
    #the messages I send to the UI
    success_message = request.args.get('success_message', None)
    error_message = request.args.get('error_message', None)

    return render_template('unroasted.html', unroasted_coffee_list=unroasted_coffee_list, success_message=success_message, error_message=error_message)


@app.route('/dashboard')
@login_required
def dashboard():
    top_five_sold = get_top_five_sold()
    least_in_stock = get_least_in_stock()

    if top_five_sold:
        top_five_sold = json.dumps(top_five_sold.json)
    else:
        top_five_sold = "[]"
        
    if least_in_stock:
        least_in_stock = json.dumps(least_in_stock.json)
    else:
        least_in_stock = "[]"

    #print(least_in_stock)

    return render_template("dashboard.html", top_five_sold=top_five_sold, least_in_stock=least_in_stock)


@app.route('/frequent_clients')
@login_required
def freq_clients():
    return render_template("frequent_clients.html")


"""
HERE ARE GONNA BE THE THE FUNCTIONS TO PULL DATA FROM THE MODALS LIKE ADDING COFFEE
EDITING AND DELETING FROM THE DATABASE

"""

@app.route('/add_roasted_coffee', methods=['POST'])
@login_required
def add_roasted_coffee():
    if request.method == 'POST':
        try:
            name_of_the_coffee = request.form.get('name')
            amount = int(request.form.get('amount'))
            date_roasting = request.form.get('date-of-arrival')
            level_of_roast = request.form.get('roasting-level')
            order_identification = request.form.get('order-identification')

            # Check if there's unroasted coffee with the same name
            unroasted_coffee = UnroastedCoffee.query.filter_by(name=name_of_the_coffee, user_id=current_user.id).first()

            if unroasted_coffee and unroasted_coffee.amount >= amount and unroasted_coffee.user_id == current_user.id:
                # Deduct the amount from unroasted coffee
                unroasted_coffee.amount -= amount
                db.session.commit()

                # Add roasted coffee to the database
                new_roasted_coffee = RoastedCoffee(
                    name=name_of_the_coffee,
                    amount=amount,
                    roasting_date=date_roasting,
                    roasting_level=level_of_roast,
                    order_number=order_identification,
                    user_id=current_user.id
                )
                db.session.add(new_roasted_coffee)
                db.session.commit()

                success_message = "Coffee added to inventory successfully"
                return redirect(url_for('roasted', success_message=success_message))
            else:
                error_message = "Not enough unroasted coffee in inventory or the coffee name doesn't exist"
                return redirect(url_for('roasted', error_message=error_message))

        except ValueError:
            error_message = "Invalid amount value"
            return redirect(url_for('roasted', error_message=error_message))

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'Something went wrong: {str(e)}')
            error_message = "There was an error, the coffee wasn't added to inventory"
            return redirect(url_for('roasted', error_message=error_message))

        finally:
            db.session.close()
            print('The try-except is finished')

    # Redirect to the dashboard or another appropriate page after adding coffee
    return redirect(url_for('roasted'))

@app.route('/add_unroasted_coffee', methods=['POST'])
@login_required
def add_unroasted_coffee():
    if request.method == 'POST':
        try:
            name_of_the_coffee = request.form.get('name').capitalize()
            amount = request.form.get('amount')
            date_arrival = request.form.get('date-of-arrival')

            new_unroasted_coffee = UnroastedCoffee(name=name_of_the_coffee, amount=amount, arrival_date=date_arrival, user_id=current_user.id)
            #print(f"UnroastedCoffee object created: {new_unroasted_coffee}")

            db.session.add(new_unroasted_coffee)
            db.session.commit()
            success_message = "Coffee added to inventory succesfully"
            return redirect(url_for('unroasted', success_message=success_message))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'Something went wrong: {str(e)}')
            #import traceback
            #traceback.print_exc()  # Print the traceback for detailed error information
            error_message = "There was an error the Coffee wasn't added to inventory"
            return redirect(url_for('unroasted', error_message=error_message))
        finally:
            db.session.close()
            print('The try-except is finished')

    return redirect(url_for('unroasted'))



"""
GETTERS FOR THE INFO 
"""

def get_unroasted_coffee():
    unroasted_coffees = UnroastedCoffee.query.filter_by(user_id=current_user.id).all()
    return unroasted_coffees

def get_roasted_coffee():
    roasted_coffees = RoastedCoffee.query.filter_by(user_id=current_user.id).all()
    return roasted_coffees

""" 
UPDATE METHODS FOR THE INFO DATABASE
"""
@app.route('/update_unroasted_coffee/<int:coffee_id>', methods=['POST'])
@login_required
def update_unroasted_coffee(coffee_id):
    if request.method == 'POST':
        try:
            # Get the coffee to update
            coffee = UnroastedCoffee.query.get(coffee_id)

            # Update fields with the form data
            coffee.name = request.form.get('name')
            coffee.amount = request.form.get('amount')
            coffee.arrival_date = request.form.get('date-of-arrival')
            

            # Commit the changes to the database
            db.session.commit()

            success_message = "Coffee updated successfully"
            return redirect(url_for('unroasted', success_message=success_message))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'Something went wrong: {str(e)}')
            error_message = "There was an error updating the coffee"
            return redirect(url_for('unroasted', error_message=error_message))
        finally:
            db.session.close()

    # Handle non-POST requests appropriately, you might want to redirect to an error page or handle it differently
    return redirect(url_for('unroasted'))


@app.route('/update_roasted_coffee/<int:coffee_id>', methods=['POST'])
@login_required
def update_roasted_coffee(coffee_id):
    if request.method == 'POST':
        try:
            # Get the coffee to update
            coffee = RoastedCoffee.query.get(coffee_id)

            # Check if the coffee object exists
            if coffee is None:
                raise NoResultFound("Coffee not found")

            before_amount = coffee.amount
            old_name = coffee.name  # Save the original name

            # Update fields with the form data
            coffee.name = request.form.get('name')
            coffee.amount = request.form.get('amount')
            coffee.roasting_date = request.form.get('roasting-date')
            coffee.order_number = request.form.get('order-identification')
            coffee.roasting_level = request.form.get('roasting-level')

            if before_amount > int(coffee.amount):
                coffee.amount_sold += (before_amount - int(coffee.amount))

            else:
                # Deduct the amount from unroasted coffee with the original name
                unroasted_coffee = UnroastedCoffee.query.filter_by(name=old_name, user_id=current_user.id).first()

                if (int(unroasted_coffee.amount) - int(coffee.amount) > 0):
                    unroasted_coffee.amount -= (before_amount - int(coffee.amount))
                    db.session.commit()
                else:
                    db.session.rollback()
                    error_message = "not enough unroasted coffee"
                    return redirect(url_for('roasted', error_message=error_message))

            # Commit the changes to the database
            db.session.commit()

            success_message = "Coffee updated successfully"
            return redirect(url_for('roasted', success_message=success_message))
        except NoResultFound:
            db.session.rollback()
            error_message = "Coffee not found"
            return redirect(url_for('roasted', error_message=error_message))
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f'Something went wrong: {str(e)}')
            error_message = "There was an error updating the coffee"
            return redirect(url_for('roasted', error_message=error_message))
        finally:
            db.session.close()

    # Handle non-POST requests appropriately
    return redirect(url_for('roasted'))


""" 
DELETE METHODS TO DELETE ROWS FROM THE DATABASE
"""

@app.route('/delete_unroasted_coffee/<int:coffee_id>', methods=['POST'])
@login_required
def delete_unroasted_coffee(coffee_id):
    admin_password = request.form.get('adminPassword')

    try:
        if current_user.check_password(admin_password):
            coffee = UnroastedCoffee.query.get(coffee_id)

            if coffee:
                db.session.delete(coffee)
                db.session.commit()
                success_message = "Coffee deleted successfully"
            else:
                success_message = "Coffee not found"
        else:
            success_message = "Incorrect admin password. Deletion canceled"
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting coffee: {str(e)}")
        success_message = "An error occurred. Deletion canceled."
    finally:
        db.session.close()

    return redirect(url_for('unroasted', success_message=success_message))


@app.route('/delete_roasted_coffee/<int:coffee_id>', methods=['POST'])
@login_required
def delete_roasted_coffee(coffee_id):
    admin_password = request.form.get('adminPassword')

    try:
        if current_user.check_password(admin_password):
            coffee = RoastedCoffee.query.get(coffee_id)
            
            if coffee:
                db.session.delete(coffee)
                db.session.commit()
                success_message = "Coffee deleted successfully"
            else:
                success_message = "Coffee not found"
        else:
            success_message = "Incorrect admin password. Deletion canceled"
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error deleting coffee: {str(e)}")
        success_message = "An error occurred. Deletion canceled."
    finally:
        db.session.close()

    return redirect(url_for('roasted', success_message=success_message))

