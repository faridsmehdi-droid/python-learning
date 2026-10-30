# WhatsApp avtomatik cavab botu

Gələn WhatsApp mesajlarına açar sözlərə görə avtomatik cavab verən Python botu.
Meta-nın rəsmi **WhatsApp Business Cloud API**-sindən istifadə edir, ona görə nömrəniz bloklanmır.

## Necə işləyir

```
Müştəri mesaj yazır → Meta serveri → sizin botunuz (/webhook) → replies.json-dan cavab seçir → Meta → Müştəri
```

## 1. Meta tərəfində hazırlıq (bir dəfəlik)

1. https://developers.facebook.com → **My Apps → Create App** → növ: **Business**.
2. Tətbiqə **WhatsApp** məhsulunu əlavə edin.
3. **WhatsApp → API Setup** səhifəsində:
   - **Temporary access token**-i kopyalayın → `WHATSAPP_TOKEN`
   - **Phone number ID**-ni kopyalayın → `PHONE_NUMBER_ID`
   - "To" bölməsinə öz nömrənizi əlavə edin (test üçün).
4. **App Settings → Basic → App Secret** → `APP_SECRET`.

> Müvəqqəti token 24 saatdan sonra bitir. Daimi istifadə üçün
> **Business Settings → System Users** bölməsində daimi token yaradın.

## 2. Botu işə salmaq

```bash
cd whatsapp_bot
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # sonra .env faylını doldurun
python bot.py
```

## 3. Botu internetə açmaq

Meta botunuza internetdən çatmalıdır. Test üçün [ngrok](https://ngrok.com):

```bash
ngrok http 5000
```

Verdiyi `https://....ngrok-free.app` ünvanını götürün.
Daimi istifadə üçün botu Render, Railway və ya VPS-də yerləşdirin.

## 4. Webhook-u qoşmaq

**WhatsApp → Configuration → Webhook → Edit**:
- **Callback URL**: `https://<ünvanınız>/webhook`
- **Verify token**: `.env`-dəki `VERIFY_TOKEN` ilə eyni söz

Sonra **Webhook fields** siyahısında **messages**-ə abunə olun (Subscribe).

İndi test nömrənizdən "salam" yazın, bot cavab verəcək.

## Cavabları dəyişmək

`replies.json` faylını redaktə edin, botu yenidən başlatmaq lazım deyil:

```json
{
  "keywords": ["çatdırılma", "catdirilma"],
  "reply": "Çatdırılma Bakı daxilində pulsuzdur."
}
```

- Açar sözlər böyük/kiçik hərfə həssas deyil.
- İlk uyğun gələn qayda işləyir.
- Heç biri uyğun gəlməsə, `default` cavabı göndərilir.

## Testlər

```bash
pip install pytest
python -m pytest
```

## Bilməli olduqlarınız

- Müştəri sizə yazandan sonra **24 saat** ərzində istənilən mətnlə cavab verə bilərsiniz.
  Bu müddətdən sonra yalnız Meta-nın təsdiqlədiyi **şablon (template)** mesajları göndərmək olar.
- Hazırda bot yalnız **mətn** mesajlarına cavab verir (şəkil, səs və s. nəzərə alınmır).
- `.env` faylını heç vaxt GitHub-a yükləməyin (`.gitignore`-da var).
