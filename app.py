from flask import Flask, render_template, request, redirect, url_for, flash
from database import db
from models import Donor, Cause, DonationTransaction

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///donation.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "donationhub-secret-key"

db.init_app(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/donors')
def donors():
    all_donors = Donor.query.all()
    return render_template('donors.html', donors=all_donors)


@app.route('/donors/add', methods=['GET', 'POST'])
def add_donor():

    if request.method == 'POST':
        existing_donor = Donor.query.filter_by(
            email=request.form['email']
        ).first()

        if existing_donor:
            flash("A donor with this email already exists.", "error")
            return redirect(url_for('add_donor'))

        new_donor = Donor(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            pincode=request.form.get('pincode'),
            date_of_birth=request.form.get('date_of_birth'),
            gender=request.form.get('gender'),
            blood_group=request.form.get('blood_group')
        )

        db.session.add(new_donor)
        db.session.commit()

        return redirect(url_for('donors'))

    return render_template('add_donor.html')


@app.route('/donors/edit/<int:id>', methods=['GET', 'POST'])
def edit_donor(id):
    donor = Donor.query.get_or_404(id)

    if request.method == 'POST':
        existing_donor = Donor.query.filter(
            Donor.email == request.form['email'],
            Donor.id != donor.id
        ).first()

        if existing_donor:
            flash("A donor with this email already exists.", "error")
            return redirect(url_for('edit_donor', id=id))

        donor.first_name = request.form['first_name']
        donor.last_name = request.form['last_name']
        donor.email = request.form['email']
        donor.phone = request.form['phone']
        donor.address = request.form.get('address')
        donor.city = request.form.get('city')
        donor.state = request.form.get('state')
        donor.pincode = request.form.get('pincode')
        donor.date_of_birth = request.form.get('date_of_birth')
        donor.gender = request.form.get('gender')
        donor.blood_group = request.form.get('blood_group')

        db.session.commit()

        return redirect(url_for('donors'))

    return render_template('edit_donor.html', donor=donor)


@app.route('/causes/edit/<int:id>', methods=['GET', 'POST'])
def edit_cause(id):
    cause = Cause.query.get_or_404(id)

    if request.method == 'POST':
        try:
            target_amount = float(request.form['target_amount'])
        except ValueError:
            flash("Please enter a valid target amount.", "error")
            return redirect(url_for('edit_cause', id=id))

        if target_amount <= 0:
            flash("Target amount must be greater than zero.", "error")
            return redirect(url_for('edit_cause', id=id))

        cause.name = request.form['name']
        cause.description = request.form.get('description')
        cause.target_amount = target_amount
        cause.category = request.form.get('category')
        cause.location = request.form.get('location')
        cause.start_date = request.form.get('start_date')
        cause.end_date = request.form.get('end_date')

        db.session.commit()

        flash("Cause updated successfully.", "success")
        return redirect(url_for('causes'))

    return render_template('edit_cause.html', cause=cause)


@app.route('/causes/delete/<int:id>', methods=['POST'])
def delete_cause(id):
    cause = Cause.query.get_or_404(id)

    existing_transactions = DonationTransaction.query.filter_by(
        cause_id=cause.id
    ).first()

    if existing_transactions:
        flash(
            "This cause cannot be deleted because donation transactions are associated with it.",
            "error"
        )
        return redirect(url_for('causes'))

    db.session.delete(cause)
    db.session.commit()

    flash("Cause deleted successfully.", "success")
    return redirect(url_for('causes'))


@app.route('/donors/delete/<int:id>', methods=['POST'])
def delete_donor(id):
    donor = Donor.query.get_or_404(id)

    existing_transactions = DonationTransaction.query.filter_by(
        donor_id=donor.id
    ).first()

    if existing_transactions:
        flash(
            "This donor cannot be deleted because donation transactions are associated with them.",
            "error"
        )
        return redirect(url_for('donors'))

    db.session.delete(donor)
    db.session.commit()

    flash("Donor deleted successfully.", "success")
    return redirect(url_for('donors'))

@app.route('/causes')
def causes():
    all_causes = Cause.query.all()
    return render_template('causes.html', causes=all_causes)

@app.route('/causes/add', methods=['GET', 'POST'])
def add_cause():
    if request.method == 'POST':
        try:
            target_amount = float(request.form['target_amount'])
        except ValueError:
            flash("Please enter a valid target amount.", "error")
            return redirect(url_for('add_cause'))

        if target_amount <= 0:
            flash("Target amount must be greater than zero.", "error")
            return redirect(url_for('add_cause'))

        new_cause = Cause(
            name=request.form['name'],
            description=request.form.get('description'),
            target_amount=target_amount,
            category=request.form.get('category'),
            location=request.form.get('location'),
            start_date=request.form.get('start_date'),
            end_date=request.form.get('end_date')
        )

        db.session.add(new_cause)
        db.session.commit()

        flash("Cause added successfully.", "success")
        return redirect(url_for('causes'))

    return render_template('add_cause.html')


@app.route('/transactions')
def transactions():
    all_transactions = DonationTransaction.query.all()

    return render_template(
        'transactions.html',
        transactions=all_transactions
    )


@app.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction():
    all_donors = Donor.query.all()
    all_causes = Cause.query.all()

    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
        except ValueError:
            flash("Please enter a valid donation amount.", "error")
            return redirect(url_for('add_transaction'))

        if amount <= 0:
            flash("Donation amount must be greater than zero.", "error")
            return redirect(url_for('add_transaction'))

        receipt_number = request.form.get('receipt_number') or None

        if receipt_number:
            existing_receipt = DonationTransaction.query.filter_by(
                receipt_number=receipt_number
            ).first()

            if existing_receipt:
                flash(
                    "A transaction with this receipt number already exists.",
                    "error"
                )
                return redirect(url_for('add_transaction'))

        new_transaction = DonationTransaction(
            donor_id=int(request.form['donor_id']),
            cause_id=int(request.form['cause_id']),
            amount=amount,
            payment_method=request.form.get('payment_method'),
            receipt_number=receipt_number
        )

        cause = Cause.query.get(int(request.form['cause_id']))

        if cause is not None:
            cause.collected_amount = (
                cause.collected_amount or 0
            ) + amount

        db.session.add(new_transaction)
        db.session.commit()

        flash("Transaction added successfully.", "success")
        return redirect(url_for('transactions'))

    return render_template(
        'add_transaction.html',
        donors=all_donors,
        causes=all_causes
    )

@app.route('/transactions/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = DonationTransaction.query.get_or_404(id)

    all_donors = Donor.query.all()
    all_causes = Cause.query.all()

    if request.method == 'POST':
        old_amount = transaction.amount
        old_cause_id = transaction.cause_id

        try:
            new_amount = float(request.form['amount'])
        except ValueError:
            flash("Please enter a valid donation amount.", "error")
            return redirect(url_for('edit_transaction', id=id))

        if new_amount <= 0:
            flash("Donation amount must be greater than zero.", "error")
            return redirect(url_for('edit_transaction', id=id))
        new_cause_id = int(request.form['cause_id'])

        old_cause = Cause.query.get(old_cause_id)

        if old_cause is not None:
            old_cause.collected_amount = (
                old_cause.collected_amount or 0
            ) - old_amount

        new_cause = Cause.query.get(new_cause_id)

        if new_cause is not None:
            new_cause.collected_amount = (
                new_cause.collected_amount or 0
            ) + new_amount

        transaction.donor_id = int(request.form['donor_id'])
        transaction.cause_id = new_cause_id
        transaction.amount = new_amount
        transaction.payment_method = request.form.get('payment_method')
        transaction.receipt_number = (
            request.form.get('receipt_number') or None
        )

        db.session.commit()

        flash("Transaction updated successfully.", "success")
        return redirect(url_for('transactions'))

    return render_template(
        'edit_transaction.html',
        transaction=transaction,
        donors=all_donors,
        causes=all_causes
    )

@app.route('/transactions/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = DonationTransaction.query.get_or_404(id)

    cause = Cause.query.get(transaction.cause_id)

    if cause is not None:
        cause.collected_amount = (
            cause.collected_amount or 0
        ) - transaction.amount

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted successfully.", "success")
    return redirect(url_for('transactions'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)