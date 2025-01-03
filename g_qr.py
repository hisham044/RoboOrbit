import qrcode
from PIL import Image

# Text to encode in QR code
data_new = "2018JM013"

# Generate QR code
qr_new = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr_new.add_data(data_new)
qr_new.make(fit=True)

# Create an image from the QR code
qr_img = qr_new.make_image(fill="black", back_color="white")

# Open the background image
bg_img = Image.open("qr/bg.jpg")

# Calculate the size of the QR code (adjustable size based on bg image)
qr_width, qr_height = qr_img.size
bg_width, bg_height = bg_img.size

# Adjust QR code size as needed (e.g., 30% of the background width)
qr_size = min(int(bg_width * 0.55), int(bg_height * 0.55))

# Resize the QR code image
qr_img = qr_img.resize((qr_size, qr_size))

# Calculate the position to place the QR code in the center of the background image
qr_x = (bg_width - qr_size) // 2
qr_y = (bg_height - qr_size) // 2 - 50
 
# Paste the QR code onto the background image
bg_img.paste(qr_img, (qr_x, qr_y))

# Save the final image
bg_img.save(f"qr/qrcode_{data_new}_on_bg.png")

print("done")
