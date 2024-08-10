from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


print(bcrypt.generate_password_hash("password123").decode("utf-8"))

hashes = ["$2b$12$rXv7JiEIof55BXCpXLjTM.wp7YAan7nmcNDyrn3OzHa2xhONmARla",
          "$2b$12$Kx3I/Xf2RnttdywYd3To.uSsx.ZjLDfJd.9HwK1i.PneJy0AkLUOG",
          "$2b$12$P4aRlCOGyJMZ6ayOLYzOluv2FN8BC41FgLPaoTXDZn2BJOvLrnhQq",
          "$2b$12$xhahsZFPVSwMR7sxUUo9ROKoRhvjKtM0N7AX2UtpwjHLjtooW8R3i"]

for h in hashes:
    print(bcrypt.check_password_hash(h, "password123"))