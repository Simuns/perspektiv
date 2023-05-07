
@app.route('/verify_status',methods=['POST', 'GET'])
def verify_status():
    if request.method == 'POST':
        session_id = request.form['session_id']
        verified_code = request.form['verification_code']
        verifyStatus = verify(verified_code, session_id)
        if verifyStatus == "verified":
            return render_template('verify_success.html')
        else:
            art = artiklar.query.filter_by(art_id=session_id).first()
            return render_template('verify.html', session_id=session_id, telefon=art.telefon, status="Kodan var skeiv, prøva umaftur!")

@app.route('/aktivera/<string:code_email>')
def aktivera(code_email):
    match = verify(code_email)
    if match == "verified":
        return("success")
    else: 
        return("false")




@app.route('/send_sms', methods=['POST'])
def send_sms():
    if request.method == 'POST':
        if app_config["verifyPhone"]:
            data = request.get_json()
            session_id = data.get('session_id')
            telefon = data.get('telefon')
            print(telefon)
            send_verification(session_id, "sms", telefon, True)
            return jsonify({'success': True}), 200
        else:
            return jsonify({'Phone number sms verification not activated': True}), 500
