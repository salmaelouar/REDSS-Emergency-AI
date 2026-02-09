
import os
import sys
sys.path.append(os.getcwd())
from app.services.database import get_db
from app.models.call import EmergencyCall
from datetime import datetime

def restore_live_calls():
    with get_db() as db:
        # Clear existing to avoid unique constraint error
        db.query(EmergencyCall).filter(EmergencyCall.call_id.in_(["LIVE_23Jan_17h52", "LIVE_23Jan_18h08"])).delete(synchronize_session=False)
        db.commit()
        
        # 1. Restore English Call
        en_call = EmergencyCall(
            call_id="LIVE_23Jan_17h52",
            transcript="""911, what's your emergency?
My dad is clutching his chest! He says he can't breathe and his left arm is numb!
What's your address, sir?
3847 Riverside Boulevard!
How old is your father?
He's 62! He's sweating really bad and he looks gray!
Is he conscious right now?
Yes, but he's doubled over! He says the pain is like an elephant sitting on his chest!
Does he have any heart problems or take heart medication?
Yes! He had a stent put in two years ago! He takes blood pressure pills!
What's his name?
Robert Martinez!
Is he sitting or lying down?
He's sitting on the couch!
Good. Keep him sitting up. Don't let him lie flat. Is he breathing good?
Really fast and shallow! He keeps saying he's going to die!
The paramedics are 3 minutes away. Stay on the line with me. Is the pain getting worse?
He's nodding yes! Oh God, please hurry!""",
            soap_subjective="The caller reports that their father is clutching his chest, cannot breathe, and has numbness in his left arm. He is sweating profusely and appears to be in significant pain, describing it as if an elephant is sitting on his chest. The father is conscious but doubled over in pain. The caller mentions that he had a stent placed years ago and is on blood pressure medication.",
            soap_objective="Name: Robert Martinez\nAge: 62\nAddress: 3847 Riverside Boulevard\nPhone: [Not provided]\nBlood: [Not provided]",
            soap_assessment="The patient is experiencing symptoms consistent with a potential cardiac event, including chest pain, shortness of breath, and left arm numbness.",
            soap_plan="Emergency medical services are en route and should assess the patient upon arrival. Advise the caller to keep the patient calm and seated, and not to let him lie flat. Monitor breathing and symptoms until help arrives.",
            urgency_level="CRITICAL",
            urgency_score=100.0,
            urgency_reasoning="Acute myocardial infarction suspected. High risk cardiovascular event with standard symptoms.",
            language="en",
            patient_name="Robert Martinez",
            disease="Medical (Cardiac)",
            created_at=datetime(2026, 1, 23, 17, 52)
        )
        
        # 2. Restore Japanese Call
        ja_call = EmergencyCall(
            call_id="LIVE_23Jan_18h08",
            transcript="""119番です。火事ですか、救急ですか?
救急です!父が胸を押さえています!息ができないと言って、左腕がしびれているんです!
住所を教えてください。
リバーサイド・ブルバード3847番地です!
お父様は何歳ですか?
62歳です!汗をすごくかいていて、顔色が灰色なんです!
意識はありますか?
はい、でも体を二つ折りにしています!痛みは象が胸の上に座っているようだと言っています!
心臓の病気はありますか?心臓の薬は飲んでいますか?
はい!2年前にステントを入れました!血圧の薬を飲んでいます!
お名前は?
ロバート・マルティネスです!
座っていますか、それとも横になっていますか?
ソファに座っています!
いいですね。座らせたままにしてください。平らに寝かせないでください。呼吸はどうですか?
すごく速くて浅いです!死ぬと何度も言っています!
救急隊が3分で到着します。電話を切らないでください。痛みは悪化していますか?
うなずいています!ああ、お願いです、急いでください!""",
            soap_subjective="患者は胸を押さえており、息ができないと訴えています。左手が指びれているとのことです。痛みが胸の上に座っているように感じています。2年前にステントを入れたことがあり、現在は血圧の薬を飲んでいます。呼吸が非常に早く、足りないと感じています。",
            soap_objective="氏名: ロバート・マルティネス\n年齢: 62歳\n住所: リバーサイドブルーバード3847番地\n電話: [不明]\n血液型: [不明]",
            soap_assessment="患者は急性の胸痛と呼吸困難を訴えており、過去に心血管の手術歴があります。症状から心筋梗塞の可能性が考えられます。",
            soap_plan="直ちに救急車を派遣し、患者の状態を監視しながら、医療機関への搬送を行う必要があります。呼吸を助けるための酸素投与を検討する。",
            urgency_level="HIGH",
            urgency_score=85.0,
            urgency_reasoning="心筋梗塞の疑い。高リスクの心臓疾患。",
            language="ja",
            patient_name="ロバート・マルティネス",
            disease="医療（心臓）",
            created_at=datetime(2026, 1, 23, 18, 8)
        )
        
        db.add(en_call)
        db.add(ja_call)
        print("✓ Restored LIVE_23Jan_17h52 (English)")
        print("✓ Restored LIVE_23Jan_18h08 (Japanese)")

if __name__ == "__main__":
    restore_live_calls()
