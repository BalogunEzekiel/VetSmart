Skip to content
Navigation Menu
BalogunEzekiel
VetSmart

Type / to search
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
VetSmart/app
/
streamlit.app.py
in
main

Edit

Preview
Indent mode

Spaces
Indent size

4
Line wrap mode

No wrap
Editing streamlit.app.py file contents
Selection deleted
180
181
182
183
184
185
186
187
188
189
190
191
192
193
194
195
196
197
198
199
200
201
202
203
204
205
206
207
208
209
210
211
212
213
214
215
216
217
218
219
220
221
222
223
224
225
226
227
228
229
230
231
232
233
234
235
236
237
238
239
240
241
242
243
244
245
246
247
248
249
250
251
252
253
    c.rect(0, height - 45, width, 45, fill=True)
    c.setFillColor(colors.white)
    c.setFont("Times-Roman", 16)
    c.drawCentredString(width / 2, height - 27, "VetSmart Diagnosis Report")

try:
    logo = Image.open("logoo.png")
    col1, col2, col3 = st.columns([1, 6, 1])  # Create columns to structure the layout    
    with col1:
        st.image(logo, width=150)  # Align logo to the left        
    with col2:
        st.markdown("<h1 style='text-align: center;'>VetSmart</h1>", unsafe_allow_html=True)  # Centralized title    
except Exception as e:
    st.warning(f"Logo could not be loaded: {e}")
    
    # Animal Information Heading beside Logo
    p = Paragraph("<b>Animal Information</b>", table_heading_style)
    p.wrapOn(c, width - 3 * inch, height)
    p.drawOn(c, width / 2 - 1.25 * inch, height - 90)

    # Animal Information Table
    animal_table_data = [
        ["Animal Tag:", animal_data["Name"]],
        ["Type:", animal_data["Type"]],
        ["Age (years):", animal_data["Age"]],
        ["Weight (kg):", animal_data["Weight"]]
    ]

    animal_table = Table(animal_table_data, colWidths=[2 * inch, 2.5 * inch], hAlign='CENTER')
    animal_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]))
    animal_table.wrapOn(c, width, height)
    animal_table.drawOn(c, width / 2 - 2.25 * inch, height - 250)

    # Diagnosis Heading
    p2 = Paragraph("<b>Diagnosis</b>", table_heading_style)
    p2.wrapOn(c, width - 2 * inch, height)
    p2.drawOn(c, width / 2 - inch, height - 290)

    # Diagnosis Table
    diagnosis_table_data = [
        ["Predicted Diagnosis:", disease],
        ["Recommendation:", recommendation]
    ]

    diagnosis_table = Table(diagnosis_table_data, colWidths=[2 * inch, 3.5 * inch], hAlign='CENTER')
    diagnosis_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEADING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT')
    ]))
    diagnosis_table.wrapOn(c, width, height)
    diagnosis_table.drawOn(c, width / 2 - 2.75 * inch, height - 380)

    # Barcode
    barcode_value = f"VS-DR-{animal_data['Name']}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    barcode = code128.Code128(barcode_value, barHeight=0.75 * inch)
    barcode_width = barcode.wrap(0, 0)[0]
    x_position = width - barcode_width - inch
    y_position = inch
    barcode.drawOn(c, x_position, y_position)
    c.setFont("Helvetica", 8)
    c.drawString(x_position, y_position - 0.2 * inch, "VetSmart Authenticated")
    c.drawString(x_position, y_position - 0.4 * inch, barcode_value)

    # Footer
    c.setFont("Helvetica", 8)
Use Control + Shift + m to toggle the tab key moving focus. Alternatively, use esc then tab to move to the next interactive element on the page.
Editing VetSmart/app/streamlit.app.py at main · BalogunEzekiel/VetSmart
