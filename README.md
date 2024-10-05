# Certbot Authenticator plugin for Websupport REST API v2

This is plugin for [Certbot](https://certbot.eff.org/). It uses Websupport [REST API v2](https://rest.websupport.sk/v2/docs) to complete dns-01 challenge.

## Usage

1. Install this plugin using `pip install certbot-dns-websupport-v2`
2. Generate Standard API access Identificator and Secret Key on your [account](https://admin.websupport.sk/sk/auth/security-settings) page
3. Get service ID from [URL](https://admin.websupport.sk/sk/service) of your service. After clicking your service you can find SERVICE_ID in your browser URL: `https://admin.websupport.sk/sk/dashboard/service/SERVICE ID`
4. Create config file `websupport.ini` with following content, replace APIKEY, SECRET and SERVICE_ID with your values.
    ```
    dns_websupport_v2_api_key = "APIKEY"
    dns_websupport_v2_secret = "SECRET"
    dns_websupport_v2_service = "SERVICE_ID"
    ```
5. For security reasons make file readable only by you. `chmod 600 websupport.ini`
6. Run certbot to generate certificates
    ```
    certbot certonly certonly --dns-websupport-v2-credentials ./websupport.ini -d *.YOUR_DOMAIN.sk --authenticator dns-websupport-v2
    ```
