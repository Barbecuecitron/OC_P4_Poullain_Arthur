# For debug purpose
def notify(txt_type, text):
    balise = ""
    if txt_type == 'ERROR':
        balise = " ! "
    elif txt_type == "SUCCESS":
        balise = ' ▼ '

    print('\n' + balise + text + balise + '\n')