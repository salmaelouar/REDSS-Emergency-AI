# Custom Test Scripts for BLEU Score Comparison
# These are your specific scripts for the "Heart Attack" scenario (Robert Martinez).

CUSTOM_CALLS = [
  # ---------------------------------------------------------
  # ENGLISH VERSION
  # ---------------------------------------------------------
  {
    "call_id": "CALL_EN_HEART_ATTACK",
    "text": """911, what's your emergency?
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
    "expected_urgency": "critical",
    "expected_type": "medical",
    "expected_location": "3847 Riverside Boulevard",
    "expected_agent": "Robert Martinez",
    "expected_soap": {
      "subjective": "The caller reports that their father, a 62-year-old male, is clutching his chest and experiencing numbness in his left arm. He is having significant difficulty breathing and describes the pain as feeling like an elephant is sitting on his chest. He is sweating profusely and appears gray in color. Medical history includes a stent placement two years ago and current use of blood pressure medication.",
      "objective": "Name: Robert Martinez\nAge: 62\nAddress: 3847 Riverside Boulevard\nPhone: [Not provided]\nBlood: [Not provided]",
      "assessment": "Acute cardiac emergency, suspected myocardial infarction (heart attack) based on symptoms and medical history.",
      "plan": "Maintain patient in sitting position; do not allow him to lie flat. Paramedics are dispatched and arriving in 3 minutes. Continuous monitoring of symptoms and breathing until EMS arrival."
    }
  },

  # ---------------------------------------------------------
  # JAPANESE VERSION (日本語版)
  # ---------------------------------------------------------
  {
    "call_id": "CALL_JA_HEART_ATTACK",
    "text": """119番です。火事ですか、救急ですか?
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
    
    # Expected answers for extraction (Gold Standard)
    "expected_urgency": "最優先",
    "expected_type": "医療",
    "expected_location": "リバーサイド・ブルバード3847番地",
    "expected_agent": "ロバート・マルティネス",
    "expected_soap": {
      "subjective": "62歳の男性。胸を押さえており、左腕のしびれと重度の呼吸困難を訴えています。痛みは「胸の上に象が座っているようだ」と表現しています。冷や汗をかいており、顔色は灰色です。2年前にステント留置術を受けており、現在は血圧の薬を服用しています。",
      "objective": "氏名: ロバート・マルティネス\n年齢: 62歳\n住所: リバーサイド・ブルバード3847番地\n電話: [不明]\n血液型: [不明]",
      "assessment": "急性心不全または心筋梗塞の疑い。緊急を要する心臓性疾患。",
      "plan": "患者をソファに座らせたまま安静を保ち、平らに寝かせないように指示。救急隊が3分以内に到着予定。到着まで意識状態と呼吸を継続的に監視する。"
    }
  }
]
