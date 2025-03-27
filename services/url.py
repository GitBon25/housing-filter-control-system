import requests

payload = {
    'sale_price__lte': 10000000,
    'area__gte': 4,
    'rooms': 3
}


cookies = {
    'ns_session': '2cb6af4c-c850-431d-97df-2c9a04d8ae70',
    'is-green-day-banner-hidden': 'true', 
    'is-ddf-banner-hidden': 'true', 
    'logoSuffix': '', 
    'iosAppAvailable': 'true', 
    'RETENTION_COOKIES_NAME': '2c3575bf7bbc468c8d8a939e7207ebc5:9NTWp-Nr1MAiujJjnznMQdL4sUw', 
    'sessionId': '62b4a199a4bd47878b4d702fa688318c:D8BDfKYRAVzfp0HUpI_mc_UnVWo', 
    'UNIQ_SESSION_ID': '51bd1e0c9153404d970ee6213f678d6f:zN8wuVU-P-ReL4zaKXoUFRGb8Kg', 
    '_sv': 'SV1.c61630e2-44c2-40c1-bc03-1d54ebb0470a.1741852032', 
    '_ym_uid': '1742887062129612119', 
    'region': '{%22data%22:{%22name%22:%22%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%22%2C%22kladr%22:%2277%22%2C%22guid%22:%221d1463ae-c80f-4d19-9331-a1b68a85b553%22}%2C%22isAutoResolved%22:true}',
    'adtech_uid': '42fb9880-516e-4bc1-90f5-fa0e6e34563c%3Adomclick.ru', 
    'top100_id': 't1.7711713.330833660.1742887063110', 
    '___dmpkit___': '79c3bac6-e401-4901-952f-6bac69f9c53f', 
    'adrcid': 'cookie_value', 
    'regionAlert': '1', 
    'tmr_lvid': '9da5a463bb07ff4abb4bb17150f2185e', 
    'tmr_lvidTS': '1742887066362', 
    'auto-definition-region': 'false', 
    'favoriteHintShowed': 'true', 
    'currentSubDomain': '', 
    'is-lotto-banner-hidden': 'true',
    'is-ddd-banner-hidden': 'true', 
    'adrdel': '1743025352272', 
    'CAS_ID': '48556048', 
    'CAS_ID_SIGNED': 'eyJleHAiOiAxNzUwOTExNDYyLCAidGd0IjogIlRHVC0zNjY2Mi1hYjk0WFllRWFVbGptY2taT1Iza01rMFMzMlpYdnNRc1VpYVNndVhPMkdPeFVid25iei1jYXMubGMiLCAiY2FzSWQiOiA0ODU1NjA0OCwgImxvZ2luVHlwZSI6ICJERUZBVUxUIiwgImxvZ2luVGltZSI6IDE3NDMwMjc0NjJ9.LMPQGIBvfRbufkhVbt7Gcn2kle3Y07YSXTXsm836p/CT3Ryc2LL1bMSxjNLGWa0+JlIVP0nb6vbAKg9xUay7uZHnfVG2HCa+FR+zgnuuKmklaSpHMtdQnkTwcVByp6ipPSO/CsvG0i+hfV8TY18HyCHAw4r3KhzqPK2uN9qH4tk=', 
    'ftgl_cookie_id': '8c917be91383db6de115d8e2533e2ac1', 
    'mland_csi_user_id': 'cef0f762-1a9f-4efa-890b-93f74951fd2c', 
    'canary-bind-id-1089': 'next', 
    'qrator_ssid2': 'v2.0.1743039965.898.b9527e50OtmCWX12|BuetpML7rQDQRGMF|7iawhV2REFf6QMa7Y5jEJSsTNC9PgD25y31wCBi8EegFyOT76D0zB2sJ+QtXybF/9X+uqBZpyRgTe32gTb7ouQ==-ODXIu7gk/TCcwq9P11UiFv0UWxg=',
    '_sas.2c534172f17069dd8844643bb4eb639294cd4a7a61de799648e70dc86bc442b9': 'SV1.c61630e2-44c2-40c1-bc03-1d54ebb0470a.1741852032.1743039968', 
    'canary-bind-id-1091': 'next', 
    '_sas': 'SV1.c61630e2-44c2-40c1-bc03-1d54ebb0470a.1741852032.1743039970', 
    '_visitId': 'f6c0cda7-6006-401d-9977-8e2bf8309507-71cba892a3bde1c',
    'isPartnerTopline': '1',
    'qrator_jsid2': 'v2.0.1743039965.898.b9527e50OtmCWX12|E40egheB1C1MwOCM|6aIaam4T9CRPDCPP76SCElb5m70VEacjvtK+V7OcUH/lkfhN8VGES7OruRTMc9xHPGV68MrG1U1g46Xx9BXyqSMS7o6BLjTQBef8HEk/MNO9TM657EXWrdxOzzxm6bEHmBepDcp09stMevaak750hmFGlolupJ08gtMS4DSoPA4=-QqzeEt+lq+v/HTHFSFpabjhxfBQ=',
    'IsShowedLikesOnboarding': 'true',
    'cookieAlert': '1',
    '_ym_isad': '2',
    'tmr_detect': '0%7C1743041936724',
    'currentRegionGuid': '619fd4a7-2e28-4d8e-b333-d1c7324c94be',
    'currentLocalityGuid': '09b74a8a-e195-493d-b776-fb00c9b763bd',
    'regionName': '09b74a8a-e195-493d-b776-fb00c9b763bd:%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%B2%D0%BE%D1%81%D1%82%D0%BE%D0%BA',
    'tmr_reqNum': '335',
    't3_sid_7711713': 's1.1753395186.1743039970460.1743043558494.5.218.11.1'
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}
url = 'https://vladivostok.domclick.ru/search'

r = requests.get(url, params=payload, cookies=cookies,headers=headers)
with open('url.html', 'w', encoding='utf-8') as f:
    f.write(r.content.decode('utf-8'))
