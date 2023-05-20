คำสั่งสำหรับผู้ใช้ทั่วไป:

<code>/img</code>: สร้างภาพจากข้อความภาษาไทย
<br>
<code>/tokens</code>: ตรวจสอบจำนวน tokens ที่คุณมี
<br>
<code>/user</code>: แสดง User ID ของคุณ
<br>
<code>/buytoken</code>: แสดงลิงค์เว็บไซต์เติมเงิน
<br>
<code>/history</code>: ดูประวัติการสนทนาของคุณ
<br>
<code>/addcoupon</code>: เติม tokens โดยใช้รหัสคูปอง
<br>
<br>
คำสั่งสำหรับผู้ดูแลระบบ:
<br>
<br>
<code>/createcoupon <จำนวน> <โทเค็น></code>: สร้างคูปอง tokens
<br>
<code>/addadmin</code>: เพิ่มผู้ดูแลระบบใหม่
<br>
<code>/totaluser</code>: แสดงจำนวนผู้ใช้ทั้งหมด
<br>
<code>/usetoken</code>: ตรวจสอบจำนวน tokens ที่ถูกใช้ในช่วงเวลาที่กำหนด
  <br>
การติดตั้งโค้ดนี้อย่างละเอียดจะทำตามขั้นตอนต่อไปนี้:
<br>
1. ติดตั้ง Python
<br>
ต้องการ Python 3.6 ขึ้นไป ถ้ายังไม่มี Python ในเครื่องคุณ สามารถดาวน์โหลดได้ที่ python.org และติดตั้งตามขั้นตอน
<br>
2. สร้าง Virtual Environment (เพิ่มเติม)
<br>
การสร้าง virtual environment จะช่วยให้การจัดการ dependencies สำหรับโปรเจคนี้สะดวกขึ้น คุณสามารถสร้างได้โดยใช้คำสั่ง:
<br>

<code>python3 -m venv myenv</code>
  <br>
และทำการ activate ด้วยคำสั่ง:
<br>
สำหรับ Windows: myenv\Scripts\activate
  <br>
สำหรับ Unix หรือ MacOS: source myenv/bin/activate
  <br>
3. ติดตั้ง Dependencies
  <br>

เมื่อคุณมี Python และ (ถ้าเลือก) virtual environment ก็สามารถติดตั้ง dependencies ด้วย pip ได้ คำสั่งติดตั้ง:
<br>

<code>pip install openai flask line-bot-sdk pymongo</code>
  <br>
4. ตั้งค่าสภาพแวดล้อม
<br>
สร้างไฟล์ .env ใน directory ของโปรเจค และเพิ่มตัวแปรสภาพแวดล้อมดังนี้:
<br>
makefile
<br>
<code>OPENAI_API_KEY=your_openai_key
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
MONGODB_URI=your_mongodb_uri</code>
  <br>
5. ติดตั้งและตั้งค่า MongoDB
<br>
ถ้าคุณยังไม่มี MongoDB คุณสามารถดาวน์โหลดและติดตั้งได้ที่ mongodb.com ตามคำแนะนำที่กำหนดไว้
<br>
6. เริ่ม Flask Server
<br>
เมื่อทำตามขั้นตอนทั้งหมดแล้ว คุณสามารถเริ่มต้นเซิร์ฟเวอร์ Flask ได้ด้วยคำสั่ง:
<br>
<code>flask run</code>
  <br>
7. ตั้งค่า Webhook สำหรับ LINE
<br>
เข้าสู่ LINE Developer Console และตั้งค่า URL สำหรับ webhook ของคุณ เพื่อที่ LINE จะสามารถส่งข้อความจากผู้ใช้ไปยังเซิร์ฟเวอร์ Flask ของคุณได้<br>

ตรวจสอบว่า LINE สามารถเข้าถึงเซิร์ฟเวอร์ Flask ของคุณได้ อาจต้องการใช้เครื่องมืออื่น ๆ เช่น ngrok เพื่อสร้าง tunnel ไปยังเซิร์ฟเวอร์ในเครื่องคอมพิวเตอร์ของคุณ<br>

ขั้นตอนเหล่านี้เป็นขั้นตอนพื้นฐานในการตั้งค่าและเริ่มต้นเซิร์ฟเวอร์ Flask ที่จะทำงานกับ LINE Messaging API อย่างไรก็ตาม คุณอาจต้องปรับแต่งการตั้งค่าต่าง ๆ ให้เหมาะสมกับความต้องการของคุณ<br>
