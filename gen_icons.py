import os
import urllib.request
import re
from PIL import Image, ImageDraw, ImageFont

def get_font(size):
    font_path = "Fraunces-Bold.ttf"
    if not os.path.exists(font_path):
        print("Downloading Fraunces font...")
        urls = [
            "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/static/Fraunces_144pt-Bold.ttf",
            "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/static/Fraunces_9pt-Bold.ttf",
            "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf"
        ]
        downloaded = False
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response, open(font_path, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"Downloaded from {url}")
                downloaded = True
                break
            except Exception as e:
                print(f"Failed {url}: {e}")
        
        if not downloaded:
            # Fallback via Google Fonts CSS requesting TTF
            try:
                css_url = "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700"
                req = urllib.request.Request(css_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    css = response.read().decode('utf-8')
                match = re.search(r'url\((https://[^)]+\.(?:ttf|woff))\)', css)
                if match:
                    font_url = match.group(1)
                    req2 = urllib.request.Request(font_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req2, timeout=10) as response, open(font_path, 'wb') as out_file:
                        out_file.write(response.read())
                    downloaded = True
            except Exception as e:
                print(f"Failed CSS fallback: {e}")
    try:
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"Could not load {font_path} ({e}), trying system/default...")
        try:
            return ImageFont.truetype("georgiab.ttf", size)
        except:
            return ImageFont.load_default()

def create_icon(size, filename, rounded=False):
    print(f"Creating {filename} ({size}x{size})...")
    scale = 4
    s_size = size * scale
    img = Image.new("RGBA", (s_size, s_size), (0, 0, 0, 0))
    
    # Draw gradient background (145deg roughly diagonal)
    grad = Image.new("RGB", (256, 256))
    g_draw = ImageDraw.Draw(grad)
    for y in range(256):
        for x in range(256):
            t = (x / 255.0 + y / 255.0) / 2.0
            r = int(0xb9 * (1 - t) + 0x8f * t)
            g = int(0xa6 * (1 - t) + 0x74 * t)
            b = int(0xe3 * (1 - t) + 0xc9 * t)
            g_draw.point((x, y), fill=(r, g, b))
    
    grad = grad.resize((s_size, s_size), Image.Resampling.BICUBIC)
    
    if rounded:
        mask = Image.new("L", (s_size, s_size), 0)
        m_draw = ImageDraw.Draw(mask)
        radius = int(s_size * 0.3125)
        m_draw.rounded_rectangle([(0, 0), (s_size - 1, s_size - 1)], radius=radius, fill=255)
        
        final_bg = Image.new("RGBA", (s_size, s_size), (0, 0, 0, 0))
        final_bg.paste(grad, (0, 0), mask=mask)
        img = final_bg
        draw = ImageDraw.Draw(img)
    else:
        img.paste(grad, (0, 0))
        draw = ImageDraw.Draw(img)
        
    font_size = int(s_size * 0.46)
    font = get_font(font_size)
    text = "G2"
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (s_size - text_w) / 2 - bbox[0]
    y = (s_size - text_h) / 2 - bbox[1]
    
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    img.save(filename, "PNG")
    print(f"Saved {filename}")

if __name__ == "__main__":
    create_icon(192, "icon-192.png", rounded=True)
    create_icon(512, "icon-512.png", rounded=True)
    create_icon(512, "maskable-icon-512.png", rounded=False)
    create_icon(180, "apple-touch-icon.png", rounded=False)
    create_icon(32, "favicon.png", rounded=True)
    print("All icons generated successfully.")
