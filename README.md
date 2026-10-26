# Project_2_Hi-Five
## https://github.com/niradaa-art/Project_2_Hi-Five/blob/main/final-MiniProject_Part2_BigData_Hi_Five.ipynb
NYC 311 Service Requests - Resolution Time Prediction Dashboard
โปรเจกต์วิเคราะห์ข้อมูลขนาดใหญ่ (Big Data Analytics) และสร้างโมเดล Machine Learning เพื่อคาดการณ์ระยะเวลาในการปิดเรื่องร้องเรียน (resolution_time) ของระบบ NYC 311 ในนครนิวยอร์ก ประจำปี 2025 โดยกลุ่ม Hi-Five

📌 1. สรุปภาพรวมโปรเจกต์ (Project Overview)
ชุดข้อมูล: NYC 311 Service Requests (1 มกราคม – 31 ธันวาคม 2025)

จำนวนข้อมูลเริ่มต้น: 3,655,042 แถว | 8 คอลัมน์ (ขนาดประมาณ 905.53 MB)

จำนวนข้อมูลหลัง Data Cleaning: 3,599,858 แถว | 15 คอลัมน์ (Retention Rate: 98.49%)

ประเภทงาน (Task Type): Regression (ทำนายระยะเวลาปิดเรื่องในหน่วยชั่วโมง)

ตัวแปรเป้าหมาย (Target): resolution_time (คำนวณจาก closed_date - created_date)

📈 2. สรุปผลการวิเคราะห์ข้อมูล (EDA & Key Insights)
พฤติกรรมการกระจายของ Target (resolution_time):

ค่ามัธยฐาน (Median): ~5.51 - 6.62 ชั่วโมง

ค่าเฉลี่ย (Mean): ~123.37 - 238.70 ชั่วโมง

ลักษณะข้อมูล: ข้อมูลมีการกระจายแบบเบ้ขวาอย่างมาก (Right-skewed) เรื่องร้องเรียนส่วนใหญ่ได้รับการแก้ไขในระยะเวลาอันสั้น แต่มีบางกรณีที่ใช้เวลานานมาก (Long tail)

Outliers (เกณฑ์ IQR): พบประมาณ 15.3% - 16.0% ซึ่งโปรเจกต์ตัดสินใจ ไม่ลบออก เนื่องจากเป็นเหตุการณ์ที่เกิดขึ้นจริงในการดำเนินงานของภาครัฐ

ปัจจัยที่มีผลต่อระยะเวลาปิดเรื่อง:

ประเภทเรื่องร้องเรียน (complaint_type): ปัญหาประเภท Noise หรือ Illegal Parking มักได้รับการจัดการอย่างรวดเร็ว (Median < 2 ชั่วโมง) ในขณะที่ปัญหาประเภท UNSANITARY CONDITION, PLUMBING, หรือ PAINT/PLASTER ใช้เวลานานกว่ามาก (Median > 160 ชั่วโมง)

หน่วยงานที่รับผิดชอบ (agency): หน่วยงานตำรวจ (NYPD) มีระยะเวลาตอบสนองเร็วที่สุดเมื่อเทียบกับหน่วยงานด้านที่อยู่อาศัย (HPD) หรือสาธารณสุข

ช่วงเวลาที่รับแจ้ง (hour / day_of_week / season): มีรูปแบบความหนาแน่นและระยะเวลาดำเนินการแตกต่างกันตามช่วงเวลาของวันและฤดูกาล

⚙️ 3. การเตรียมข้อมูลและโมเดล (ML Pipeline & Leakage Audit)
การแบ่งข้อมูล (Data Splitting): แบ่งข้อมูลตามลำดับเวลาเพื่อป้องกัน Data Leakage

Train Set: มกราคม – สิงหาคม 2025

Validation Set: กันยายน – ตุลาคม 2025

Test Set: พฤศจิกายน – ธันวาคม 2025

การป้องกัน Data Leakage: ใช้เฉพาะตัวแปรที่ทราบ ณ เวลารับแจ้งเรื่องเท่านั้น (complaint_type, agency, borough, hour, day_of_week, month, season) และไม่ใช้คอลัมน์สถานะเรื่อง (status) เป็น Feature
