import qrcode

# Text to encode in QR code
data_new = "2019JF055"

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
img_new = qr_new.make_image(fill="black", back_color="white")

# Save the image
img_new.save(f"qr/qrcode_{data_new}.png")

print("done")
