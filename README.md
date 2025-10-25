# Elite Barber Shop - AI Receptionist Agent

A conversational AI agent that helps customers book appointments at a barber shop. Built with pure Python (no frameworks) and powered by OpenAI's GPT-4 model.

## Features

### Core Features (Required)
- **Pure Python Implementation** - No LangChain, CrewAI, or other frameworks
- **Multi-turn Conversations** - Maintains context throughout the conversation
- **4 Essential Tools**:
  - `get_business_info()` - Get salon information (hours, contact, address)
  - `get_services()` - Retrieve services and pricing
  - `check_availability()` - Check available time slots
  - `book_appointment()` - Book appointments with customer details
- **OpenAI Integration** - Uses GPT-4 model for natural language processing

### Bonus Features
- **Streamlit Web Interface** - Beautiful web-based chat interface
- **Email Confirmation** - Mock email sending for appointments
- **Appointment Management** - JSON-based appointment storage

## Project Structure

```
barber-appointment-agent/
├── agent.py              # Main agent with conversation loop
├── tools.py              # Tool functions for agent
├── app.py                # Streamlit web interface
├── data/
│   ├── services.json     # Services and pricing data
│   ├── calendar.json     # Mock appointment calendar
│   └── business_info.json # Business information
├── appointments.json     # Booked appointments (auto-created)
├── requirements.txt      # Python dependencies
├── env_example.txt       # Environment variables template
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd barber-appointment-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file and add your OpenAI API key
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Run the Application

#### Option A: Terminal Interface
```bash
python agent.py
```

#### Option B: Web Interface (Recommended)
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

## How It Works

### Agent Architecture

The system follows a simple but effective agent architecture:

1. **User Input** → Agent receives customer message
2. **Intent Recognition** → Agent determines what the customer wants
3. **Tool Selection** → Agent chooses appropriate tools to use
4. **Tool Execution** → Agent calls tools to get information
5. **Response Generation** → Agent processes results and responds
6. **Context Maintenance** → Agent remembers conversation history

### Tool System

The agent uses 4 core tools:

```python
# Get business information
get_business_info("hours")  # Returns working hours
get_business_info("contact")  # Returns phone/contact info
get_business_info("address")  # Returns business address

# Get all services and prices
get_services()  # Returns complete service menu

# Check availability
check_availability("2025-01-13", 45)  # Check 45-min slots for Jan 13

# Book appointment
book_appointment(
    customer_name="John Doe",
    customer_phone="+1234567890",
    customer_email="john@example.com",
    date="2025-01-13",
    time="14:00",
    services=["Saç Kesimi", "Sakal Düzeltme"],
    total_price=225.0,
    duration_minutes=45
)
```

## Example Conversations

### Scenario 1: Successful Booking

```
USER: Merhaba, yarın randevu alabilir miyim?
AGENT: Merhaba! Tabii ki yardımcı olabilirim. Hangi hizmetimizden yararlanmak istersiniz?

USER: Saç kesimi ve sakal düzeltme istiyorum
AGENT: [Calls get_services() and check_availability()]
Saç kesimi (30 dk, 150 TL) ve sakal düzeltme (15 dk, 75 TL) için toplam 45 dakikalık randevu gerekiyor. Yarın için müsait saatlerimiz:
- 09:00
- 11:30
- 14:00
- 16:30
Hangi saat sizin için uygun?

USER: 14:00 olabilir
AGENT: Mükemmel, 14:00 için ayırtabilirim. Lütfen isim, telefon numarası ve email adresinizi paylaşır mısınız?

USER: Adım Mehmet Yılmaz, tel: 0532-555-1234, email: mehmet@example.com
AGENT: [Calls book_appointment() and send_email_confirmation()]
🎉 Randevunuz başarıyla oluşturuldu!
📅 Tarih: 13 Ekim 2025, Saat 14:00
✂ Hizmetler: Saç Kesimi, Sakal Düzeltme
💰 Toplam: 225 TL
🆔 Randevu numaranız: APT-20251013-001
Email adresinize onay mesajı gönderdim. Başka bir konuda yardımcı olabilir miyim?
```

### Scenario 2: Information Request

```
USER: Fiyatlarınız nedir?
AGENT: [Calls get_services()]
İşte hizmetlerimiz ve fiyatlarımız:
✂ Saç Kesimi - 150 TL (30 dk)
🧔 Sakal Düzeltme - 75 TL (15 dk)
💧 Saç Yıkama - 50 TL (10 dk)
✨ Cilt Bakımı - 200 TL (45 dk)
Randevu almak ister misiniz?
```

## Technical Details

### Dependencies

- `openai>=1.0.0` - OpenAI API client
- `streamlit>=1.28.0` - Web interface framework
- `python-dotenv>=1.0.0` - Environment variable management

### Data Storage

- **JSON Files**: All data is stored in JSON format for simplicity
- **Appointments**: Stored in `appointments.json`
- **Calendar**: Mock calendar in `data/calendar.json`
- **Services**: Service catalog in `data/services.json`

### API Integration

The agent uses OpenAI's GPT-4 model for:
- Natural language understanding
- Intent recognition
- Response generation
- Tool call extraction

## Web Interface Features

The Streamlit interface provides:

- **Beautiful UI** - Modern, responsive design
- **Real-time Chat** - Instant messaging experience
- **Quick Actions** - One-click buttons for common requests
- **Business Info Sidebar** - Always-visible salon information
- **Recent Appointments** - View recent bookings
- **Mobile Friendly** - Works on all devices

## Customization

### Adding New Services

Edit `data/services.json`:

```json
{
  "services": [
    {
      "name": "New Service",
      "price": 100,
      "duration_minutes": 30,
      "description": "Service description"
    }
  ]
}
```

### Modifying Business Hours

Edit `data/business_info.json`:

```json
{
  "working_hours": "09:00-20:00",
  "hours": {
    "monday": "09:00-20:00",
    "tuesday": "09:00-20:00"
  }
}
```

### Adding New Tools

1. Add function to `tools.py`
2. Register in `AVAILABLE_TOOLS` dictionary
3. Update agent's system prompt

## Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ❌ Please set OPENAI_API_KEY environment variable
   ```
   **Solution**: Set your OpenAI API key in `.env` file

2. **Module Not Found**
   ```
   ModuleNotFoundError: No module named 'openai'
   ```
   **Solution**: Install dependencies with `pip install -r requirements.txt`

3. **Port Already in Use**
   ```
   Port 8501 is already in use
   ```
   **Solution**: Use `streamlit run app.py --server.port 8502`

## Future Enhancements

- [ ] **Database Integration** - Replace JSON with PostgreSQL/MySQL
- [ ] **Real Email Service** - Integrate with SendGrid/AWS SES
- [ ] **Calendar Integration** - Connect with Google Calendar
- [ ] **Payment Processing** - Add Stripe/PayPal integration
- [ ] **Multi-language Support** - Support for English, Turkish, etc.
- [ ] **Voice Interface** - Add speech-to-text capabilities
- [ ] **Analytics Dashboard** - Track appointment metrics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for the GPT-4 API
- Streamlit for the web framework
- The AI community for inspiration and best practices

