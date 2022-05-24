import time
import httpx
import asyncio
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/sync_form', methods=['GET', 'POST'])
def sync_form():
    _time = 0
    errors = {}
    if request.method == 'POST':
        start = time.time()
        request_form = request.form

        if not request_form['firstName']:
            errors['firstName'] = "First name is required"
        if not request_form['lastName']:
            errors['lastName'] = "Last name is required"
        
        email_res = httpx.get(f"https://api.eva.pingutil.com/email?email={request_form['email']}").json()
        if 'data' in email_res and not email_res['data']['deliverable']:
            errors['email'] = "Email is not deliverable"

        postal_code_res = httpx.get(f"https://api.postalpincode.in/pincode/{request_form['zip']}").json()[0]
        print(postal_code_res)
        if postal_code_res['Status'].lower() in ["Error", "404"]:
            errors['zip'] = "Postal code is invalid"
        
        countries_res = httpx.get("https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates.json").json()
        for country in countries_res:
            if country['name'] == "India":
                for state in country['states']:
                    if state['name'] == request_form['state']:
                        break
                else:
                    errors['state'] = "State is invalid"
                    break

        _time = "{:.3f}".format(time.time() - start)
        print(f"Time taken: {_time}")

    return render_template('form.html', title="Sync Form", errors=errors, form=request.form, _time=_time)


@app.route('/async_form', methods=['GET', 'POST'])
async def async_form():
    _time = 0
    errors = {}
    if request.method == 'POST':
        start = time.time()
        request_form = request.form

        if not request_form['firstName']:
            errors['firstName'] = "First name is required"
        if not request_form['lastName']:
            errors['lastName'] = "Last name is required"
        
        async with httpx.AsyncClient() as client:
            email_res, postal_code_res, countries_res = await asyncio.gather(
                client.get(f"https://api.eva.pingutil.com/email?email={request_form['email']}"),
                client.get(f"https://api.postalpincode.in/pincode/{request_form['zip']}"),
                client.get("https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/countries%2Bstates.json")
            )
        
        email_res = email_res.json()
        postal_code_res = postal_code_res.json()[0]
        countries_res = countries_res.json()

        if 'data' in email_res and not email_res['data']['deliverable']:
            errors['email'] = "Email is not deliverable"

        if postal_code_res['Status'].lower() in ["Error", "404"]:
            errors['zip'] = "Postal code is invalid"
        
        for country in countries_res:
            if country['name'] == "India":
                for state in country['states']:
                    if state['name'] == request_form['state']:
                        break
                else:
                    errors['state'] = "State is invalid"
                    break

        _time = "{:.3f}".format(time.time() - start)
        print(f"Time taken: {_time}")

    return render_template('form.html', title="Async Form", errors=errors, form=request.form, _time=_time)



async def fetch_url(client, url):
    """Fetch the specified URL using the aiohttp client specified."""
    response = await client.get(url)
    return {'url': response.url, 'status': response.status_code}

@app.route('/async_get_urls')
async def async_get_urls():
    async with httpx.AsyncClient() as client:
        r1, r2, r3 = await asyncio.gather(
            fetch_url(client, 'https://picsum.photos/200/300?random=1'),
            fetch_url(client, 'https://picsum.photos/200/300?random=2'),
            fetch_url(client, 'https://picsum.photos/200/300?random=3'),
        )
    return jsonify({'r1': r1['status'], 'r2': r2['status'], 'r3': r3['status']})