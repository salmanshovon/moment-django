import smtplib

try:
    with smtplib.SMTP_SSL('aranyait.com.bd', 465) as server:  # or SMTP() for TLS
        server.login('no-reply@aranyait.com.bd', 'callmeg0dfatherT00')
        print("✅ SMTP Authentication Successful!")
except Exception as e:
    print(f"❌ SMTP Error: {e}")