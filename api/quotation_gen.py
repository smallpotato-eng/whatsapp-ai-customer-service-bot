from fpdf import FPDF
import os, base64
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "quotations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONT = "C:/Windows/Fonts/msjh.ttc"
FONT_BOLD = "C:/Windows/Fonts/msjhbd.ttc"

LABELS = {
    "zh-hk": {
        "title": "報價單", "date": "日期", "valid": "有效期至",
        "contact": "聯絡電話", "ref": "參考編號",
        "subtotal": "小計", "shipping": "運費", "total": "合計",
        "item": "產品", "qty": "數量", "unit_price": "單價", "amount": "金額",
        "age": "年齡", "coverage": "保障類型", "premium": "估計保費",
        "prop_type": "物業類型", "transaction": "交易類型",
        "district": "地區", "size": "面積（呎）", "est_price": "估計價格",
        "commission": "佣金估算（1%）",
        "disclaimer": "此報價僅供參考，實際費用以最終確認為準。",
        "thankyou": "感謝您的查詢，如有疑問請隨時聯絡我們。",
        "free": "免費",
        "treatment": "療程項目", "sessions": "次數", "skin_concern": "肌膚問題",
        "skin_type": "膚質", "recommendation": "美容師建議", "package": "套餐優惠",
        "beauty_title": "專屬美容療程報價",
    },
    "zh-cn": {
        "title": "报价单", "date": "日期", "valid": "有效期至",
        "contact": "联系电话", "ref": "参考编号",
        "subtotal": "小计", "shipping": "运费", "total": "合计",
        "item": "产品", "qty": "数量", "unit_price": "单价", "amount": "金额",
        "age": "年龄", "coverage": "保障类型", "premium": "估计保费",
        "prop_type": "物业类型", "transaction": "交易类型",
        "district": "地区", "size": "面积（尺）", "est_price": "估计价格",
        "commission": "佣金估算（1%）",
        "disclaimer": "此报价仅供参考，实际费用以最终确认为准。",
        "thankyou": "感谢您的查询，如有疑问请随时联系我们。",
        "free": "免费",
        "treatment": "疗程项目", "sessions": "次数", "skin_concern": "肌肤问题",
        "skin_type": "肤质", "recommendation": "美容师建议", "package": "套餐优惠",
        "beauty_title": "专属美容疗程报价",
    },
    "en": {
        "title": "Quotation", "date": "Date", "valid": "Valid Until",
        "contact": "Contact", "ref": "Reference No.",
        "subtotal": "Subtotal", "shipping": "Shipping", "total": "Total",
        "item": "Item", "qty": "Qty", "unit_price": "Unit Price", "amount": "Amount",
        "age": "Age", "coverage": "Coverage Type", "premium": "Est. Premium",
        "prop_type": "Property Type", "transaction": "Transaction",
        "district": "District", "size": "Size (sq ft)", "est_price": "Est. Price",
        "commission": "Est. Commission (1%)",
        "disclaimer": "This quotation is for reference only. Final price subject to confirmation.",
        "thankyou": "Thank you for your enquiry. Feel free to contact us anytime.",
        "free": "Free",
        "treatment": "Treatment", "sessions": "Sessions", "skin_concern": "Skin Concern",
        "skin_type": "Skin Type", "recommendation": "Therapist's Recommendation", "package": "Package Deal",
        "beauty_title": "Personalised Beauty Treatment Quotation",
    }
}

BUSINESSES = {
    "insurance": {
        "name": "SecureLife Insurance",
        "address": "20/F, SecureLife Tower, 100 Des Voeux Rd, Central, HK",
        "tel": "2888-9999",
        "email": "info@securelife.com.hk",
        "color": (39, 174, 96),
        "logo": "SL",
    },
    "realestate": {
        "name": "PrimeHome Realty",
        "address": "15/F, PrimeHome Centre, 1 Canton Rd, Tsim Sha Tsui, KLN",
        "tel": "3456-7890",
        "email": "info@primehome.com.hk",
        "color": (230, 126, 34),
        "logo": "PH",
    },
    "shop": {
        "name": "MiaMart Online Shop",
        "address": "www.miamart.com.hk",
        "tel": "—",
        "email": "cs@miamart.com.hk",
        "color": (142, 68, 173),
        "logo": "MM",
    },
    "beauty": {
        "name": "ABC Aesthetics",
        "address": "G/F, Beauty Plaza, 88 Orchard Ave",
        "tel": "012-345-6789",
        "email": "hello@abcaesthetics.com",
        "color": (198, 120, 150),
        "logo": "ABC",
    },
}


class QuotePDF(FPDF):
    def __init__(self, biz_key, lang):
        super().__init__()
        self.biz = BUSINESSES.get(biz_key, BUSINESSES["shop"])
        self.lang = lang if lang in LABELS else "en"
        self.L = LABELS[self.lang]
        self._setup_fonts()
        self.set_auto_page_break(auto=True, margin=20)

    def _setup_fonts(self):
        has_cjk = os.path.exists(FONT) and os.path.exists(FONT_BOLD)
        if has_cjk:
            self.add_font("R", fname=FONT)
            self.add_font("B", fname=FONT_BOLD)
            self.fn_r, self.fn_b = "R", "B"
        else:
            self.fn_r, self.fn_b = "Helvetica", "Helvetica"

    def _set_r(self, size=11): self.set_font(self.fn_r, size=size)
    def _set_b(self, size=11): self.set_font(self.fn_b, size=size)

    def header(self):
        biz = self.biz
        c = biz["color"]
        # Logo block
        self.set_fill_color(*c)
        self.rect(10, 10, 28, 28, "F")
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 18)
        self._set_b(14)
        self.cell(28, 10, biz["logo"], align="C")
        # Company info
        self.set_text_color(30, 30, 30)
        self.set_xy(42, 10)
        self._set_b(13)
        self.cell(0, 7, biz["name"])
        self.set_xy(42, 18)
        self._set_r(9)
        self.cell(0, 6, biz["address"])
        self.set_xy(42, 25)
        self.cell(0, 6, f"Tel: {biz['tel']}  |  {biz['email']}")
        # Divider
        self.set_draw_color(*c)
        self.set_line_width(0.8)
        self.line(10, 41, 200, 41)
        self.ln(35)

    def footer(self):
        self.set_y(-28)
        self.set_draw_color(*self.biz["color"])
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self._set_r(8)
        self.set_text_color(120, 120, 120)
        self.multi_cell(0, 5, self.L["disclaimer"], align="C")
        self.cell(0, 5, self.L["thankyou"], align="C")

    def _title_row(self):
        self._set_b(20)
        self.set_text_color(*self.biz["color"])
        self.cell(0, 10, self.L["title"], align="C")
        self.ln(12)

    def _info_row(self, label, value):
        self._set_b(10)
        self.set_text_color(80, 80, 80)
        self.cell(55, 7, label + ":", border="B")
        self._set_r(10)
        self.set_text_color(30, 30, 30)
        self.cell(0, 7, str(value), border="B")
        self.ln(8)

    def _section(self, title):
        self.ln(4)
        self.set_fill_color(*self.biz["color"])
        self.set_text_color(255, 255, 255)
        self._set_b(10)
        self.cell(0, 7, f"  {title}", fill=True)
        self.ln(9)
        self.set_text_color(30, 30, 30)

    def _table_header(self, cols):
        self.set_fill_color(240, 240, 240)
        self._set_b(9)
        self.set_text_color(60, 60, 60)
        widths = [90, 25, 35, 40]
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=True, align="C")
        self.ln()

    def _table_row(self, row):
        self._set_r(9)
        self.set_text_color(30, 30, 30)
        widths = [90, 25, 35, 40]
        aligns = ["L", "C", "R", "R"]
        for i, val in enumerate(row):
            self.cell(widths[i], 7, str(val), border=1, align=aligns[i])
        self.ln()

    def _total_row(self, label, value, bold=False):
        if bold:
            self._set_b(11)
            self.set_text_color(*self.biz["color"])
        else:
            self._set_r(10)
            self.set_text_color(60, 60, 60)
        self.cell(150, 8, label, align="R")
        self.cell(40, 8, str(value), align="R", border="B" if bold else "")
        self.ln(9)

    def build_meta(self, phone):
        ref = f"QT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        today = datetime.now().strftime("%Y-%m-%d")
        valid = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        self._title_row()
        self._info_row(self.L["ref"], ref)
        self._info_row(self.L["date"], today)
        self._info_row(self.L["valid"], valid)
        self._info_row(self.L["contact"], phone)

    # --- Insurance ---
    def build_insurance(self, phone, q):
        self.add_page()
        self.build_meta(phone)
        self._section(self.L["title"])
        self._info_row(self.L["age"], q.get("age", "—"))
        self._info_row(self.L["coverage"], q.get("coverage_type", "—"))
        premium = q.get("premium_estimate", "—")
        unit = self.L["per_month"] if "/月" in str(q.get("unit", "/月")) or "month" in str(q.get("unit", "")) else "/月"
        self._info_row(self.L["premium"], f"HKD {premium} {unit}" if premium != "—" else "—")

    # --- Real Estate ---
    def build_realestate(self, phone, q):
        self.add_page()
        self.build_meta(phone)
        self._section(self.L["title"])
        self._info_row(self.L["transaction"], q.get("transaction_type", "—"))
        self._info_row(self.L["prop_type"], q.get("property_type", "—"))
        self._info_row(self.L["district"], q.get("district", "—"))
        size = q.get("size_sqft", "")
        if size:
            self._info_row(self.L["size"], f"{size} {self.L.get('sqft','sq ft')}")
        price = q.get("estimated_price", "")
        if price:
            price_val = int(str(price).replace(",", ""))
            commission = f"HKD {price_val * 0.01:,.0f}"
            self._info_row(self.L["est_price"], f"HKD {price_val:,}")
            self._info_row(self.L["commission"], commission)

    # --- Beauty ---
    def build_beauty(self, phone, q):
        self.add_page()
        # Decorative banner
        c = self.biz["color"]
        self.set_fill_color(*c)
        self.rect(0, 0, 210, 6, "F")
        self.set_fill_color(255, 240, 245)
        self.rect(0, 6, 210, 3, "F")

        self.build_meta(phone)

        # Client info section
        self._section(self.L.get("beauty_title", "Beauty Treatment Quotation"))
        if q.get("skin_type"):
            self._info_row(self.L.get("skin_type", "Skin Type"), q["skin_type"])
        if q.get("skin_concern"):
            self._info_row(self.L.get("skin_concern", "Skin Concern"), q["skin_concern"])

        # Treatment table
        treatments = q.get("treatments", [])
        if treatments:
            self.ln(3)
            # Table header with beauty color
            self.set_fill_color(*c)
            self.set_text_color(255, 255, 255)
            self._set_b(9)
            widths = [80, 25, 35, 50]
            headers = [
                self.L.get("treatment", "Treatment"),
                self.L.get("sessions", "Sessions"),
                self.L.get("unit_price", "Unit Price"),
                self.L.get("amount", "Amount")
            ]
            for i, h in enumerate(headers):
                self.cell(widths[i], 8, h, border=1, fill=True, align="C")
            self.ln()

            subtotal = 0
            row_colors = [(255, 245, 250), (255, 255, 255)]
            for idx, t in enumerate(treatments):
                name = t.get("name", "Treatment")
                sessions = int(t.get("sessions", 1))
                price = float(t.get("price", 0))
                amt = sessions * price
                subtotal += amt
                self.set_fill_color(*row_colors[idx % 2])
                self._set_r(9)
                self.set_text_color(30, 30, 30)
                self.cell(widths[0], 7, name, border=1, fill=True)
                self.cell(widths[1], 7, str(sessions), border=1, fill=True, align="C")
                self.cell(widths[2], 7, f"RM {price:.0f}", border=1, fill=True, align="R")
                self.cell(widths[3], 7, f"RM {amt:.0f}", border=1, fill=True, align="R")
                self.ln()

            self.ln(3)

            # Package discount
            discount = float(q.get("discount", 0))
            if discount > 0:
                self._total_row(self.L.get("subtotal", "Subtotal"), f"RM {subtotal:.0f}")
                self._total_row(self.L.get("package", "Package Deal"), f"- RM {discount:.0f}")
                total = subtotal - discount
            else:
                total = subtotal

            self._total_row(self.L.get("total", "Total"), f"RM {total:.0f}", bold=True)

        # Recommendation box
        recommendation = q.get("recommendation", "")
        if recommendation:
            self.ln(6)
            self.set_fill_color(255, 240, 245)
            self.set_draw_color(*c)
            self.set_line_width(0.5)
            self.rect(10, self.get_y(), 190, 22, "DF")
            self.set_xy(14, self.get_y() + 3)
            self._set_b(9)
            self.set_text_color(*c)
            self.cell(0, 5, f"*  {self.L.get('recommendation', 'Recommendation')}")
            self.ln(6)
            self.set_x(14)
            self._set_r(9)
            self.set_text_color(60, 60, 60)
            self.multi_cell(182, 5, recommendation)

        # Bottom floral divider
        self.ln(4)
        self.set_text_color(*c)
        self._set_r(10)
        self.cell(0, 6, "~ ~ ~", align="C")

    # --- Shop ---
    def build_shop(self, phone, q):
        self.add_page()
        self.build_meta(phone)
        self._section(self.L["title"])
        items = q.get("items", [])
        if items:
            self._table_header([self.L["item"], self.L["qty"], self.L["unit_price"], self.L["amount"]])
            subtotal = 0
            for item in items:
                name = item.get("name", "Item")
                qty = int(item.get("qty", 1))
                price = float(item.get("price", 0))
                amt = qty * price
                subtotal += amt
                self._table_row([name, qty, f"${price:.0f}", f"${amt:.0f}"])
            self.ln(2)
            shipping = float(q.get("shipping", 30 if subtotal < 300 else 0))
            shipping_label = self.L["free"] if shipping == 0 else f"HKD {shipping:.0f}"
            total = subtotal + shipping
            self._total_row(self.L["subtotal"], f"HKD {subtotal:.0f}")
            self._total_row(self.L["shipping"], shipping_label)
            self._total_row(self.L["total"], f"HKD {total:.0f}", bold=True)


def generate_quote(business_type, phone, quote_data, lang="zh-hk"):
    pdf = QuotePDF(business_type, lang)
    builder = {
        "insurance": pdf.build_insurance,
        "realestate": pdf.build_realestate,
        "shop": pdf.build_shop,
        "beauty": pdf.build_beauty,
    }.get(business_type)

    if not builder:
        return None

    builder(phone, quote_data)

    filename = f"quote_{phone}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    path = OUTPUT_DIR / filename
    pdf.output(path)

    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    return {"path": path, "filename": filename, "base64": b64}
