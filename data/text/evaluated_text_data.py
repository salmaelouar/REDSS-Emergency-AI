EVALUATED_CALLS = [
  {
    "call_id": "CALL_101",
    "text": """911, what's your emergency?
[Man, voice tight with panic] My dad is clutching his chest! He says he can't breathe and his left arm is numb!
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
Does he have aspirin in the house?
[Frantic] Yes, in the kitchen! Should I get it?
Yes! Have him chew one regular aspirin if he can swallow. Is he sitting or lying down?
He's sitting on the couch! [Yelling] Dad, chew this aspirin!
Good. Keep him sitting up. Don't let him lie flat. How's his breathing?
[Panicked] Really fast and shallow! He keeps saying he's going to die!
The paramedics are 3 minutes away. Stay on the line with me. Is the pain getting worse?
[Dad groaning in background] He's nodding yes! Oh God, please hurry!""",
    "expected_urgency": "critical",
    "expected_type": "medical",
    "expected_location": "3847 Riverside Boulevard",
    "expected_agent": "Robert Martinez",
    "expected_soap": {
      "subjective": "62-year-old male with acute chest pain radiating to left arm, described as crushing/pressure sensation, severe dyspnea, diaphoresis, sense of impending doom",
      "objective": "Patient conscious, sitting position, tachypneic, diaphoretic, gray appearance, history of coronary artery disease with prior stent placement, on antihypertensive medication, aspirin administered",
      "assessment": "Acute myocardial infarction (probable STEMI), cardiac emergency",
      "plan": "ALS response with cardiac monitoring, 12-lead EKG, oxygen therapy, IV access, nitroglycerin consideration, immediate transport to cardiac catheterization-capable facility, STEMI alert activation"
    }
  },
  {
    "call_id": "CALL_102",
    "text": """911, what's your emergency?
[Woman screaming, incoherent] Help! Help me! I can't stop the bleeding!
Ma'am, I need you to calm down and tell me what happened. What's your address?
[Sobbing, hyperventilating] 5612 Oakmont Drive! My husband cut himself with the chainsaw!
Where is he cut?
[Screaming] His leg! Oh God, there's blood everywhere! I can see inside his leg!
Is your husband conscious?
[Yelling at husband] Stay awake! Talk to me! [To dispatcher] Yes, but he's really pale!
What's his name?
David! David Chen!
I need you to grab towels or clothes and put pressure directly on the wound. Can you do that?
[Crying] I'm trying! The blood just keeps coming! It's spurting out!
That means it hit an artery. Press harder. Use both hands if you need to.
[Sobbing] I am! David, baby, stay with me! [To dispatcher] He's closing his eyes!
Keep talking to him! Don't let him go to sleep! Paramedics are 4 minutes away!
[Panicked] David! Open your eyes! Look at me! [To dispatcher] He's so cold!
That's from blood loss. Keep that pressure on. You're doing great.
[Crying] There's so much blood! The whole floor is covered!
I know it's scary but you're helping him. Stay on the line with me.""",
    "expected_urgency": "critical",
    "expected_type": "medical",
    "expected_location": "5612 Oakmont Drive",
    "expected_agent": "David Chen",
    "expected_soap": {
      "subjective": "Adult male with traumatic laceration to lower extremity from chainsaw, arterial bleeding present, altered level of consciousness",
      "objective": "Patient conscious but lethargic, severe hemorrhage with arterial spurting, direct pressure being applied by spouse, signs of hypovolemic shock (pallor, hypothermia, altered mentation), significant blood loss at scene",
      "assessment": "Traumatic arterial injury with class III/IV hemorrhagic shock, life-threatening emergency",
      "plan": "ALS trauma response, tourniquet application if direct pressure fails, rapid IV access with blood products, aggressive fluid resuscitation, immediate transport to trauma center, activate massive transfusion protocol, possible surgical intervention"
    }
  },
  {
    "call_id": "CALL_103",
    "text": """911, what's your emergency?
[Teenage girl, screaming and crying] My little brother is having a seizure and he won't stop shaking!
What's your address?
[Sobbing] 2847 Willow Creek Court!
How old is your brother?
He's 5! This has never happened before!
How long has he been seizing?
[Panicked] I don't know! Maybe 5 minutes? He's still doing it!
What's his name?
Tommy! Tommy Williams!
Is there anything in his mouth?
[Crying] No! Should I put something in there?
No, don't put anything in his mouth. Is he on his side?
[Panicked] No, he's on his back! He's turning blue!
Roll him onto his side right now. Can you do that?
[Grunting] Okay, I got him on his side!
Good job. Move anything away from him that he could hit. Are your parents home?
[Crying] No! They're at the store! I'm the babysitter! Is he going to die?
The paramedics are 2 minutes away. Is he still seizing?
[Sobbing] Yes! His whole body is shaking! There's foam coming from his mouth!
That's okay. Just stay with him. Make sure he stays on his side. Did he have a fever today?
[Crying] I don't know! He seemed fine when I got here!
Okay, help is almost there. Stay on the line with me.""",
    "expected_urgency": "critical",
    "expected_type": "medical",
    "expected_location": "2847 Willow Creek Court",
    "expected_agent": "Tommy Williams (5 years old)",
    "expected_soap": {
      "subjective": "5-year-old male with first-time seizure, duration greater than 5 minutes, ongoing at time of call, no known seizure history",
      "objective": "Patient experiencing prolonged generalized tonic-clonic seizure, cyanosis present, oral secretions/foam noted, positioned on side by caregiver, parents absent, babysitter present",
      "assessment": "Status epilepticus, life-threatening prolonged seizure activity, possible febrile seizure or new-onset epilepsy",
      "plan": "ALS pediatric seizure protocol, benzodiazepine administration, airway management with oxygen, rapid transport to pediatric-capable ED, neurological evaluation, possible intubation if seizure continues, workup for infection and metabolic causes"
    }
  },
  {
    "call_id": "CALL_104",
    "text": """911, what's your emergency?
[Young man, breathless] My girlfriend is having an asthma attack and her inhaler isn't working!
What's your address?
4521 Maple Street, apartment 2B!
How long has she been having trouble breathing?
About 15 minutes! She's used her inhaler three times but she's getting worse!
What's her name?
Jessica! Jessica Park!
Can she speak in full sentences?
[Pause] Jess, can you talk? [To dispatcher] She can only say a few words at a time!
Is she sitting up?
Yes, she's sitting on the edge of the bed leaning forward.
Can you see if her lips or fingernails are turning blue?
[Worried] Yeah, her lips look a little blue!
Is she on any other medications for asthma?
She has a steroid inhaler but I don't know if she's been taking it.
Okay. Tell her to try to slow her breathing down. Breathe in through the nose, out through the mouth.
[To girlfriend] Slow breaths, baby. [To dispatcher] She's trying but she's panicking!
I know. Paramedics are 4 minutes out. Is she wheezing? Can you hear it?
[Pause] Yeah, I can hear it from across the room. It's really loud.
Has she had attacks this bad before?
[Scared] She told me she was hospitalized for asthma when she was a teenager.
Okay, that's important. Keep her sitting up and stay with her. They're almost there.""",
    "expected_urgency": "high",
    "expected_type": "medical",
    "expected_location": "4521 Maple Street, apartment 2B",
    "expected_agent": "Jessica Park",
    "expected_soap": {
      "subjective": "Adult female with acute severe asthma exacerbation, rescue inhaler used 3 times without relief, 15-minute progressive worsening, history of asthma hospitalization",
      "objective": "Patient in respiratory distress, unable to speak in complete sentences, audible wheezing, cyanosis present (lips), tripod positioning, tachypneic, possible medication non-compliance with controller medications",
      "assessment": "Acute severe asthma exacerbation, possible status asthmaticus",
      "plan": "ALS response with nebulized bronchodilators (albuterol/ipratropium), oxygen supplementation, systemic corticosteroids, IV access, continuous monitoring, transport to ED, possible ICU admission, compliance assessment"
    }
  },
  {
    "call_id": "CALL_105",
    "text": """911, what's your emergency?
[Woman, voice shaking] My mother fell and hit her head. There's a lot of blood and she seems confused.
What's your address?
7123 Birchwood Avenue.
How old is your mother?
She's 78. She takes blood thinners for her heart.
What blood thinner does she take?
Warfarin. She's been on it for years.
When did she fall?
Just a few minutes ago. Maybe 5 minutes?
Where did she hit her head?
On the corner of the coffee table. There's a big gash on her forehead.
Is she conscious?
Yes, but she keeps asking me the same questions over and over. She doesn't remember falling.
What's her name?
Linda. Linda Thompson.
Is the bleeding controlled?
I'm holding a towel on it but it's still bleeding through. Should I press harder?
Yes, keep firm pressure on it. Did you see her fall?
[Voice breaking] Yes, she just suddenly collapsed. One second she was standing, then she was on the floor.
Did she say anything before she fell? Did she feel dizzy or have chest pain?
She said she felt lightheaded, but then she just went down.
Is she having any trouble moving her arms or legs?
[Pause] Mom, can you squeeze my hand? [To dispatcher] She's squeezing, but her right side seems weaker.
Paramedics are 3 minutes away. Keep pressure on that cut and keep her still. Don't let her get up.""",
    "expected_urgency": "high",
    "expected_type": "medical",
    "expected_location": "7123 Birchwood Avenue",
    "expected_agent": "Linda Thompson",
    "expected_soap": {
      "subjective": "78-year-old female fell after feeling lightheaded, head struck coffee table edge, witnessed fall, anticoagulated with warfarin, reports ongoing bleeding from forehead laceration",
      "objective": "Patient conscious with altered mentation (repetitive questioning, no memory of event), head laceration with active bleeding despite pressure, right-sided weakness noted, on anticoagulation therapy, syncopal episode prior to fall",
      "assessment": "Head trauma in anticoagulated patient, likely intracranial hemorrhage, syncope of unknown etiology, right-sided weakness suggests neurological involvement",
      "plan": "ALS response, C-spine precautions, hemorrhage control, immediate CT head, neurosurgical consultation, INR check and possible reversal of anticoagulation, assess for stroke vs. hemorrhage, cardiac workup for syncope, ICU admission likely"
    }
  },
  {
    "call_id": "CALL_106",
    "text": """911, what's your emergency?
[Man, urgent but controlled] My wife is 38 weeks pregnant and she's having really bad contractions. They're coming every 2 minutes.
What's your address?
1829 Sunset Ridge Drive.
Is this her first baby?
No, it's our third. The last one came really fast.
How fast?
We barely made it to the hospital. She was in labor for like 45 minutes total.
What's her name?
Maria. Maria Santos.
Can I talk to her?
[Woman's voice, strained] Hello? [Groaning] Oh God, here comes another one!
Maria, how long have you been having contractions?
[Breathing heavily] Since about 20 minutes ago. They started strong right away!
Do you feel like you need to push?
[Panicked] I don't know! Maybe? There's so much pressure! [Groaning loudly]
Can you check if you see the baby's head? Don't be embarrassed, I need to know.
[Husband] I'll check. [Pause] Oh my God! I can see the top of the baby's head!
Okay, the baby is coming now. Do NOT try to hold it in. Get clean towels and blankets.
[Man panicked] Should I call an ambulance or drive?
The ambulance is already coming, 4 minutes out. Get those towels NOW.
[Woman screaming] I have to push! I can't stop it!
That's okay, Maria! Push with the contraction. Your husband is going to catch the baby.""",
    "expected_urgency": "critical",
    "expected_type": "medical",
    "expected_location": "1829 Sunset Ridge Drive",
    "expected_agent": "Maria Santos",
    "expected_soap": {
      "subjective": "38-week pregnant female, gravida 3 para 2, rapid onset of frequent contractions (every 2 minutes), history of precipitous labor, strong urge to push, contractions started 20 minutes prior",
      "objective": "Baby crowning, imminent delivery, multiparous patient with known history of rapid labor progression, contractions frequent and strong, patient unable to delay pushing",
      "assessment": "Imminent precipitous home delivery, term pregnancy",
      "plan": "Emergency home delivery instructions provided, paramedic response for immediate postpartum care, infant assessment including APGAR scoring, transport mother and newborn to hospital, monitor for complications, assess placental delivery"
    }
  },
  {
    "call_id": "CALL_107",
    "text": """911, what's your emergency?
[Older man, steady voice] Hello, I'm a retired nurse. My wife is diabetic and I believe she's having a severe low blood sugar reaction.
What's your address, sir?
6234 Elmwood Court.
What makes you think it's low blood sugar?
She's confused, sweating profusely, and shaking. She can barely stay awake. I checked her glucose and it's 38.
That's very low. What's her name?
Dorothy. Dorothy Miller. She's 69.
Did she eat today?
She had breakfast around 7 AM, but it wasn't much. Then she took her full insulin dose at 8.
How long has she been symptomatic?
I noticed about 15 minutes ago. She's getting worse quickly.
Were you able to give her any sugar?
I tried orange juice but she can't swallow well right now. She keeps pushing it away and she's very lethargic.
Does she have a glucagon kit?
Yes, but it expired last year. Should I still use it?
In this situation, yes. Do you know how to administer it?
Yes, I'm giving it now. [Pause] Okay, it's injected in her thigh.
Good. That should start working in about 10 minutes. How's her breathing?
Normal rate and depth. But she's very pale and cold to the touch.
Paramedics are 5 minutes away. Turn her on her side in case she vomits.
Already done. Her eyes are fluttering. I think she's trying to respond.
That's good. You did everything right.""",
    "expected_urgency": "critical",
    "expected_type": "medical",
    "expected_location": "6234 Elmwood Court",
    "expected_agent": "Dorothy Miller",
    "expected_soap": {
      "subjective": "69-year-old female with insulin-dependent diabetes, blood glucose 38 mg/dL, altered mental status, took full insulin dose with inadequate food intake, symptoms progressing over 15 minutes",
      "objective": "Patient lethargic with altered level of consciousness, diaphoretic, tremulous, unable to safely swallow, hypothermic, positioned on side by caregiver (retired nurse), expired glucagon administered IM by trained caregiver",
      "assessment": "Severe hypoglycemia with altered consciousness, insulin overdose relative to intake",
      "plan": "ALS response with glucose monitoring, IV dextrose administration, reassess response to glucagon, continuous monitoring, transport for observation and insulin regimen adjustment, diabetes education"
    }
  },
  {
    "call_id": "CALL_108",
    "text": """911, what's your emergency?
[Woman, moderately concerned] My teenage son fell off his skateboard and hurt his arm. I think it might be broken.
What's your address?
4782 Pinecrest Lane.
How old is your son?
He's 15. His name is Kyle.
What happened exactly?
He was doing tricks at the skate park and fell. He landed on his left arm.
Can I talk to him?
[Teenage boy, in pain] Yeah, hi. Ow, it really hurts.
Kyle, can you describe where it hurts?
It's my forearm, between my wrist and elbow. It's swelling up really bad.
Can you move your fingers?
[Pause] Yeah, but it hurts to try.
Did you hit your head or lose consciousness?
No, I was wearing a helmet. I just fell on my arm.
Is the bone sticking out through the skin?
[Grossed out] No, but it looks really weird. Like bent.
That's called a deformity. Don't try to straighten it. Can your mom get some ice?
[Mom] I already put ice on it wrapped in a towel.
Good. Kyle, are you feeling sick to your stomach or dizzy?
No, I'm okay. It just hurts a lot. Like an 8 out of 10.
We can send an ambulance, but you could also drive him to the ER if you're comfortable.
[Mom] How long would an ambulance take?
About 10 minutes. The hospital is about 8 minutes if you drive.
[Mom] We'll drive him. Should I take the ice off?
No, keep it on. Support his arm and don't let him move it.""",
    "expected_urgency": "low",
    "expected_type": "medical",
    "expected_location": "4782 Pinecrest Lane",
    "expected_agent": "Kyle (15 years old)",
    "expected_soap": {
      "subjective": "15-year-old male with left forearm injury after skateboarding fall, reports severe pain (8/10), visible deformity noted by patient and parent",
      "objective": "Alert and oriented, no loss of consciousness, helmet worn during injury, left forearm with swelling and deformity noted between wrist and elbow, able to move fingers with pain, neurovascularly intact, no open fracture, ice applied appropriately, no other injuries reported",
      "assessment": "Closed long bone fracture (likely radius/ulna), stable patient",
      "plan": "Parent transport to ED acceptable, maintain immobilization, continue ice application, orthopedic evaluation, x-ray imaging, possible closed reduction or surgical fixation, pain management"
    }
  },
  {
    "call_id": "CALL_109",
    "text": """911, what's your emergency?
[Woman, worried but calm] I'm calling about my husband. He's been having diarrhea and vomiting all day and now he's very weak.
What's your address?
9156 Woodland Drive.
How old is your husband?
He's 54. His name is Tom.
When did the symptoms start?
Early this morning, around 6 AM. He's been going to the bathroom constantly.
Has he been able to keep any fluids down?
He tried drinking water and Gatorade but it all comes right back up.
Can I speak with him?
[Man's voice, weak] Hello?
Tom, how are you feeling right now?
[Weakly] Terrible. Really dizzy. Everything hurts.
Do you have a fever?
I feel hot, but we haven't taken my temperature.
Any blood in your vomit or stool?
[Pause] No, I don't think so. Just watery.
Have you traveled recently or eaten anything unusual?
We went to a seafood buffet yesterday for our anniversary. My wife feels fine though.
When was the last time you urinated?
[Thinking] This morning, I think. Not since then.
That's concerning. Have you been sweating?
Yeah, but I also feel really cold.
Tom, you're showing signs of dehydration. We should send an ambulance.
[Weakly] Do I really need an ambulance? Can my wife just drive me?
With your symptoms, especially the dizziness and not urinating, it's safer to have paramedics evaluate you.
[Sighs] Okay, if you think that's best.""",
    "expected_urgency": "medium",
    "expected_type": "medical",
    "expected_location": "9156 Woodland Drive",
    "expected_agent": "Tom",
    "expected_soap": {
      "subjective": "54-year-old male with acute gastroenteritis, symptoms for 12+ hours, intractable vomiting and diarrhea, unable to tolerate oral intake, weakness, dizziness, subjective fever, decreased urination, recent seafood consumption",
      "objective": "Patient alert but weak, reports orthostatic symptoms, no hematochezia or hematemesis, oliguria present (last void >6 hours), signs of dehydration (dizziness, weakness, chills despite fever), wife asymptomatic",
      "assessment": "Acute gastroenteritis with moderate to severe dehydration, possible foodborne illness",
      "plan": "BLS/ALS transport for IV fluid resuscitation, antiemetics, monitor vital signs and orthostatics, laboratory evaluation including electrolytes and renal function, stool culture if indicated, rehydration protocol, monitor for hemodynamic instability"
    }
  },
  {
    "call_id": "CALL_110",
    "text": """911, what's your emergency?
[Elderly woman, calm] Hello dear, I'm calling because I've had a nosebleed for about 45 minutes and it won't stop.
What's your address, ma'am?
3421 Sycamore Boulevard, apartment 12C.
How old are you?
I'm 81. My name is Helen Reed.
Are you on any blood thinners?
Yes, I take warfarin. I have an artificial heart valve.
Have you been pinching your nose?
Yes, I've been sitting here pinching it and leaning forward like they tell you.
Which nostril is bleeding?
Just the right one. I've gone through quite a few tissues.
Have you had nosebleeds before?
Occasionally, but they usually stop in 10 or 15 minutes.
Did anything trigger this one? Did you bump your nose?
No, I was just reading my book and it started.
Are you feeling dizzy or weak?
A little lightheaded, yes. But I'm 81, dear, I'm always a bit lightheaded. [Chuckles]
Have you taken your blood pressure recently?
Not today, but it's usually on the high side. I take medicine for that too.
Helen, with the blood thinners and how long it's been bleeding, we should send someone to check on you.
[Pleasantly] Oh, I suppose that would be wise. I do live alone.
Do you have someone who can come be with you?
My daughter lives nearby. I can call her after we hang up.
The paramedics will be there in about 8 minutes. Keep pinching your nose.
Will do, dear. Thank you so much.""",
    "expected_urgency": "medium",
    "expected_type": "medical",
    "expected_location": "3421 Sycamore Boulevard, apartment 12C",
    "expected_agent": "Helen Reed",
    "expected_soap": {
      "subjective": "81-year-old female with unilateral epistaxis (right naris) for 45 minutes, on warfarin for mechanical heart valve, reports lightheadedness, history of hypertension, lives alone",
      "objective": "Patient alert and conversational, applying appropriate first aid (pinching and forward lean), prolonged bleeding despite measures, anticoagulated patient, hypertensive history, mild orthostatic symptoms reported",
      "assessment": "Prolonged epistaxis in anticoagulated elderly patient, possible posterior bleed, mild hypovolemia",
      "plan": "BLS transport for ENT evaluation, likely nasal packing needed, check INR/PT levels, blood pressure monitoring, assess for posterior vs anterior source, possible cauterization or packing, ensure family support, monitor for continued bleeding"
    }
  },
  {
    "call_id": "CALL_111",
    "text": """911, what's your emergency?
[Middle-aged man, slightly annoyed] Yeah, my elderly father refuses to go to the doctor and I'm worried about him.
What's going on with your father, sir?
He's been coughing for like three weeks now. It's getting worse and he sounds terrible.
What's your address?
5892 Highland Avenue.
How old is your father?
He's 77. Stubborn as a mule too.
Is he coughing anything up?
Yeah, he's coughing up yellow-green stuff. Sometimes it looks like there might be blood in it.
Does he have a fever?
I don't know. He won't let me take his temperature. Says he's fine.
Can I speak with him?
[Elderly man's voice, wheezy] What do you want?
Sir, your son is concerned about your cough. How long have you been sick?
[Coughing fit] I don't know, couple weeks. It's just a cold.
Are you having any trouble breathing?
[Wheezily] I'm 77 years old. Everything's hard. [Coughs]
Do you smoke?
Used to. Quit 10 years ago.
Do you have emphysema or COPD?
[Grudgingly] Yeah, I got the COPD.
When's the last time you saw your doctor?
[Defensive] I don't remember. Maybe last year.
Sir, with COPD and a cough this long with colored sputum, you should really be seen. This could be pneumonia.
[Annoyed] It's just a cough. You people want to make a big deal out of everything.
We can send paramedics to check your oxygen levels and listen to your lungs.
[Sighs heavily] Fine. Send them. But I'm not going to any hospital.""",
    "expected_urgency": "medium",
    "expected_type": "medical",
    "expected_location": "5892 Highland Avenue",
    "expected_agent": "Father (77 years old)",
    "expected_soap": {
      "subjective": "77-year-old male with productive cough for 3 weeks with yellow-green sputum and possible hemoptysis, known COPD, former smoker (quit 10 years ago), worsening symptoms, reluctant to seek care",
      "objective": "Patient audibly wheezy on phone, productive cough noted during call, possible fever status unknown, no recent medical follow-up (>1 year), patient resistant to evaluation",
      "assessment": "Acute exacerbation of COPD vs community-acquired pneumonia, possible hemoptysis, patient non-compliant with medical care",
      "plan": "Paramedic assessment including pulse oximetry, lung auscultation, vital signs, assess work of breathing, chest x-ray indicated, possible antibiotics and steroids, strong transport recommendation, patient education on complications, possible refusal of care documentation needed"
    }
  },
  {
    "call_id": "CALL_112",
    "text": """911, what's your emergency?
[Young woman, embarrassed] Um, this is kind of embarrassing, but I think I have a really bad urinary tract infection and I'm in a lot of pain.
What's your address?
2847 Riverside Terrace, apartment 5A.
What symptoms are you having?
I can barely pee, and when I do it burns really bad. And my back is killing me, like right here on my lower back.
How long have you had these symptoms?
It's been getting worse over the past three days, but today it's unbearable. I also have chills and I feel really hot.
Have you taken your temperature?
[Pause] Yeah, it's 102.3.
That's a significant fever. Are you having any nausea or vomiting?
I threw up once this morning. I thought it was just because I felt so crappy.
How old are you?
I'm 26. My name is Sarah.
Do you have any medical conditions? Diabetes, kidney problems?
No, I'm usually healthy. I've had UTIs before but never this bad.
Are you pregnant or could you be pregnant?
No, definitely not.
Is the back pain on both sides or just one?
Just the right side. It really hurts when I move.
Sarah, this sounds like it could be a kidney infection, which is more serious than a bladder infection. You need to be seen soon.
[Worried] Do I need an ambulance? Can't I just go to urgent care?
With your fever and back pain, the ER would be better. You could drive yourself if you feel okay to drive, or we can send an ambulance.
I think I can drive. Is it okay to wait a little bit? My roommate gets home in an hour.
I'd recommend going now, but if you're going to wait, drink lots of water and call back if you get worse.
Okay, I'll go now. Thank you.""",
    "expected_urgency": "medium",
    "expected_type": "medical",
    "expected_location": "2847 Riverside Terrace, apartment 5A",
    "expected_agent": "Sarah (26 years old)",
    "expected_soap": {
      "subjective": "26-year-old female with dysuria, urinary frequency, fever (102.3°F), right-sided flank pain, chills, single episode of emesis, symptoms worsening over 3 days, history of recurrent UTIs",
      "objective": "Patient alert, fever 102.3°F documented, unilateral right flank pain, no pregnancy, no comorbidities, able to ambulate, considering self-transport",
      "assessment": "Acute pyelonephritis (kidney infection), uncomplicated",
      "plan": "Patient counseled to seek ED evaluation, urinalysis and culture needed, IV antibiotics likely required, imaging (ultrasound or CT) to rule out abscess or obstruction, antipyretics, hydration, follow-up with primary care, patient opting for self-transport acceptable given stable vital signs"
    }
  },
  {
    "call_id": "CALL_113",
    "text": """911, what's your emergency?
[Man, calm] Hi, I'm calling about my neighbor. She's elderly and I haven't seen her in about four days. Her newspapers are piling up.
What's the address?
She lives at 7231 Oakwood Drive. The gray house with the white fence.
What's your neighbor's name?
Margaret Foster. She's probably in her 80s.
Have you tried knocking on her door?
Yes, several times today. Her car is in the driveway. I can see lights on inside but no one answers.
Does she have any family nearby that you know of?
I think she has a son, but I don't know how to contact him. She lives alone.
Do you know if she has any health problems?
She walks with a cane. I've seen a home health nurse visit a few times. She mentioned once that she has diabetes.
When was the last time you saw her?
Last Saturday. She waved to me when I was mowing my lawn. We usually chat when we see each other, so it's unusual not to see her for this long.
Did she seem okay the last time you saw her?
Yeah, she seemed fine. Normal.
Do you have any way to see inside her house? Any windows?
The curtains are mostly closed. I did look in the living room window and I can see the TV is on.
Okay, we'll send officers to do a welfare check. What's your name and number?
Robert Chen. My number is 555-0198. I have her spare key if they need it.
That's helpful. Officers will be there in about 15 minutes. They may contact you.
Okay, I'll be home. I'm just really worried about her.""",
    "expected_urgency": "low",
    "expected_type": "medical",
    "expected_location": "7231 Oakwood Drive",
    "expected_agent": "Margaret Foster",
    "expected_soap": {
      "subjective": "Elderly female (approximately 80s) not seen for 4 days, newspapers accumulating, known diabetes and mobility impairment (uses cane), receives home health services",
      "objective": "Welfare check requested by concerned neighbor, vehicle present at residence, lights and TV on inside, no response to knocking, last seen 4 days ago appearing normal, lives alone, neighbor has emergency key",
      "assessment": "Welfare check indicated, possible fall, medical emergency, or incapacitation in elderly high-risk patient",
      "plan": "Police welfare check with EMS standby, forced entry if necessary with neighbor's key available, assess patient condition upon entry, medical evaluation if patient located"
    }
  },
  {
    "call_id": "CALL_114",
    "text": """911, what's your emergency?
[Woman, matter-of-fact] My 3-year-old daughter stuck a bead up her nose and I can't get it out.
What's your address?
4156 Magnolia Street.
Can you see the bead?
Yes, it's right there in her left nostril. It's one of those plastic craft beads, like the size of a small pea.
Is she having any trouble breathing?
No, she's breathing fine through her mouth and the other nostril. She's actually playing right now like nothing happened.
How long has it been up there?
She told me about it maybe 20 minutes ago, but who knows when she actually did it. Could've been during her nap.
What's her name?
Emma. Emma Rodriguez.
Have you tried to remove it?
I tried with tweezers but she keeps pulling away and I'm afraid I'll push it in further.
That's good that you stopped. Is there any bleeding?
No bleeding at all. She's totally fine otherwise, just has a bead in her nose.
You have a couple options. You can bring her to urgent care or the ER, and they can remove it safely. Or we can send an ambulance.
How long would an ambulance take?
Probably about 12 minutes.
The urgent care is like 5 minutes away. I think I'll just take her there myself.
That's fine. If she starts having trouble breathing, bleeding heavily, or you can't see the bead anymore, call back immediately.
Will do. Thank you!""",
    "expected_urgency": "medium",
    "expected_type": "medical",
    "expected_location": "4156 Magnolia Street",
    "expected_agent": "Emma Rodriguez (3 years old)",
    "expected_soap": {
      "subjective": "3-year-old female with nasal foreign body (plastic bead) in left naris, time of insertion uncertain (possibly during nap), no respiratory distress, no epistaxis",
      "objective": "Foreign body visible in anterior naris, patient in good spirits and playing, breathing unobstructed, no bleeding, parent attempted removal with tweezers unsuccessfully",
      "assessment": "Nasal foreign body, stable pediatric patient, no acute distress",
      "plan": "Parent transport to urgent care acceptable, foreign body removal with appropriate instrumentation, no emergency transport required, parent educated on warning signs (respiratory distress, bleeding, foreign body no longer visible)"
    }
  },
  {
    "call_id": "CALL_115",
    "text": """911, what's your emergency?
[Teenager, trying to sound calm but worried] Hey, so my friend drank a lot at a party and I'm not sure if he's okay.
What's your address?
We're at 8923 University Boulevard. It's a house party.
How old is your friend?
We're both 18. It's his birthday actually.
How much did he drink?
I don't know exactly. He was playing beer pong and doing shots. Maybe 8 or 9 drinks over like three hours?
What's his name?
Jake. Jake Morrison.
Is he conscious?
Yeah, but he's pretty out of it. He's lying on the couch mumbling.
Can you wake him up? Can he talk to you?
[Pause] Jake! Jake, man, talk to me! [To dispatcher] He opened his eyes and said something but I couldn't understand it.
Has he thrown up?
Yeah, like 30 minutes ago. A lot. We put him on his side after that.
That's good. Is he still on his side?
Yeah, we have him on the couch on his side with a trash can.
How's his breathing?
Seems normal to me. Maybe a little slow but steady.
Are there adults at this party?
[Hesitant] No, his parents are out of town. Are we gonna get in trouble?
I'm more concerned about Jake right now. Has he taken any drugs? Pills, weed, anything else?
[Quietly] There was weed earlier but I don't think he smoked any. Just alcohol.
Given how much he drank, we should send paramedics to check on him. Alcohol poisoning is serious.
[Worried] Okay, yeah. That's probably smart. He's my best friend.
They'll be there in about 6 minutes. Keep him on his side and stay with him.""",
    "expected_urgency": "high",
    "expected_type": "medical",
    "expected_location": "8923 University Boulevard",
    "expected_agent": "Jake Morrison (18 years old)",
    "expected_soap": {
      "subjective": "18-year-old male with acute alcohol intoxication, consumed approximately 8-9 drinks over 3 hours, altered level of consciousness, history of significant emesis 30 minutes prior",
      "objective": "Patient semi-conscious with incomprehensible speech, positioned on side by peers after vomiting, respiratory rate subjectively normal but possibly bradypneic, possible poly-substance exposure (marijuana present), no adult supervision",
      "assessment": "Acute alcohol intoxication with altered mental status, aspiration risk, possible alcohol poisoning",
      "plan": "ALS response for airway protection, IV access, thiamine and dextrose administration, monitor for respiratory depression, toxicology evaluation, assess for co-ingestion, BAC measurement, transport to ED for observation"
    }
  }
]