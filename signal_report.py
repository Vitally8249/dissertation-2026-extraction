import sqlite3
from datetime import datetime
import html
import os

# Configuration
DB_PATH = 'signal_plaintext.db'
HTML_OUTPUT = 'Signal_Forensic_Extraction_Report.html'

def get_chats():
    if not os.path.exists(DB_PATH):
        print(f"[!] Error: {DB_PATH} not found in the current directory.")
        return []

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        # 1. Analyze the 'recipient' table schema
        cursor.execute("PRAGMA table_info(recipient)")
        recip_cols = [row[1] for row in cursor.fetchall()]
        
        # Build valid SQL selections (e.g., "r.e164" or standalone "NULL")
        phone_select = "r.e164" if "e164" in recip_cols else ("r.phone" if "phone" in recip_cols else "NULL")
        display_name_select = "r.system_display_name" if "system_display_name" in recip_cols else "NULL"
        profile_name_select = "r.profile_name" if "profile_name" in recip_cols else "NULL"

        # 2. Analyze the 'message' table schema
        cursor.execute("PRAGMA table_info(message)")
        msg_cols = [row[1] for row in cursor.fetchall()]
        
        # Adapt to sender mapping changes
        sender_col = "from_recipient_id" if "from_recipient_id" in msg_cols else ("address" if "address" in msg_cols else "recipient_id")

        print(f"[*] Detected Schema: Phone mapping='{phone_select}', Sender mapping='{sender_col}'")

        # 3. Dynamically build and execute the query
        query = f"""
        SELECT 
            m.date_sent, 
            {phone_select} AS phone, 
            {display_name_select} AS system_display_name, 
            {profile_name_select} AS profile_name, 
            m.body,
            m.type
        FROM message m
        LEFT JOIN recipient r ON m.{sender_col} = r._id
        WHERE m.body IS NOT NULL AND m.body != ''
        ORDER BY m.date_sent ASC
        """
        
        cursor.execute(query)
        return cursor.fetchall()
        
    except sqlite3.OperationalError as e:
        print(f"[!] SQLite Error: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

def generate_html_report(messages):
    if not messages:
        print("[!] No messages extracted. Report not generated.")
        return

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Signal Forensic Extraction Report</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; color: #333; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }
            .header h1 { margin: 0; color: #2c3e50; }
            .header p { margin: 5px 0; color: #7f8c8d; font-size: 0.9em; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }
            th, td { border: 1px solid #bdc3c7; padding: 12px; text-align: left; vertical-align: top; word-wrap: break-word; }
            th { background-color: #ecf0f1; font-weight: bold; color: #2c3e50; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .timestamp { width: 18%; font-size: 0.85em; color: #555; }
            .sender { width: 25%; font-weight: bold; color: #2980b9; }
            .message { width: 57%; }
            .meta { font-size: 0.8em; color: #7f8c8d; font-weight: normal; display: block; margin-top: 4px; }
            .footer { text-align: center; margin-top: 40px; font-size: 0.8em; color: #95a5a6; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Signal Chat Extraction Evidence</h1>
            <p>Generated on: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>Source Material: Full File System Extraction (signal.db)</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th class="timestamp">Date & Time (UTC)</th>
                    <th class="sender">Sender Information</th>
                    <th class="message">Message Content</th>
                </tr>
            </thead>
            <tbody>
    """

    for msg in messages:
        raw_date = msg['date_sent']
        phone = msg['phone']
        display_name = msg['system_display_name']
        profile_name = msg['profile_name']
        body = msg['body']
        
        # Convert timestamp to human-readable format
        try:
            if raw_date:
                date_obj = datetime.utcfromtimestamp(raw_date / 1000.0)
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            else:
                formatted_date = "Unknown Time"
        except Exception:
            formatted_date = "Invalid Format"

        # Prioritize system display name, then profile name, fallback to generic
        name_str = html.escape(display_name) if display_name else (html.escape(profile_name) if profile_name else "Unknown Contact")
        phone_str = html.escape(phone) if phone else "No Number Registered"
        
        # Sanitize message body
        safe_body = html.escape(body).replace('\n', '<br>')

        html_content += f"""
            <tr>
                <td class="timestamp">{formatted_date}</td>
                <td class="sender">
                    {name_str}<br>
                    <span class="meta">Phone: {phone_str}</span>
                </td>
                <td class="message">{safe_body}</td>
            </tr>
        """

    html_content += """
            </tbody>
        </table>
        <div class="footer">
            End of Extraction Log.
        </div>
    </body>
    </html>
    """

    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[*] Successfully parsed {len(messages)} messages.")
    print(f"[*] Evidence report saved to: {HTML_OUTPUT}")

if __name__ == "__main__":
    messages = get_chats()
    if messages:
        generate_html_report(messages)