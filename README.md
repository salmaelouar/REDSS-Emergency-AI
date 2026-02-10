# REDSS-Emergency-AI
**Rapid Emergency Data and Severity System (REDSS)**

## Project Overview
REDSS-Emergency-AI is a comprehensive AI-powered platform designed for the intelligent processing of emergency calls. It serves a dual purpose: providing immediate clinical triage support and analyzing speech patterns for underlying cognitive conditions.

The system leverages state-of-the-art NLP and machine learning to assist dispatchers and healthcare professionals in making faster, evidence-based decisions while capturing critical data for long-term patient monitoring.

## Key Capabilities

### 🚑 Emergency Triage & Documentation
- **Automated Transcription**: Uses OpenAI's Whisper for high-accuracy real-time transcription of emergency dialogues.
- **SOAP Extraction**: Automatically generates **Subjective, Objective, Assessment, and Plan** structured notes from raw transcripts.
- **Hybrid Urgency Classification**: Implements a hybrid engine that combines evidence-based medical rules with AI contextual analysis to assign **ESI (Emergency Severity Index)** levels.

### 🧠 Linguistic & Cognitive Analysis
- **Advanced Language Markers**: Analyzes speech fluency, cognitive markers, and semantic coherence to identify potential health risks.
- **Dementia Screening**: Evaluates speech rate, pause duration, filler word ratios, and lexical diversity (TTR, Guiraud’s Index) to provide a preliminary **cognitive risk assessment**.
- **Conversational Quality**: Scores calls based on Grice’s Maxims (Quantity, Quality, Relation, Manner) to assess communication effectiveness.

### 📊 Monitoring & Dashboard
- **Situational Awareness**: A React-based frontend providing a real-time overview of current calls and their severity.
- **Patient Tracking**: Aggregates history and metrics to visualize the "Patient Journey" and long-term health trends.

## Project Structure
- `src-code/`: The core application code.
  - `app/`: FastAPI backend with AI services (Urgency classification, SOAP extraction, linguistic markers).
  - `frontend/`: React-based dashboard for situational awareness and reporting.
- `docs/`: Technical reports and documentation (available in DE, EN, JA).
- `paper/`: Research papers and academic background of the system.
- `data/`: Sample audio and text transcripts for testing the pipeline.
- `videos/`: Demonstrations of the system in action.

## Getting Started
Scripts for starting the application components are located in `src-code/`:
- **Backend**: `bash start_backend.sh`
- **Frontend**: `bash start_frontend.sh`

---
*Developed as part of the REDSS project to enhance emergency response with artificial intelligence.*
