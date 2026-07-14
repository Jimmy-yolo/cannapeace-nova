# Product Images Setup Guide

## Upload Your Product Posters

Place your product poster images in the `product_images/` folder with these exact names:

```
product_images/
├── capjunky.jpg          # Capjunky strain poster
├── alien_marker.jpg      # Alien Marker strain poster
├── trop_cherry.jpg       # Trop Cherry strain poster
├── gogurtz.jpg           # Gogurtz strain poster
├── berry_bonds.jpg       # Berry Bonds strain poster
├── lcg_grapegas.jpg      # LCG x Grapegas strain poster
└── apple_banana.jpg      # Apple Banana strain poster
```

## Image Requirements

- **Format**: JPG or PNG
- **Size**: Recommended 1080x1350px (Instagram portrait format)
- **File size**: Under 1MB per image for fast loading
- **Content**: Should include:
  - Strain name
  - Price (450฿ for 10g)
  - THC percentage
  - Effects description
  - Strain type (Indica/Sativa/Hybrid)
  - Beautiful product photo

## How It Works

When customers ask about a specific strain, the bot will:
1. Send the product poster image
2. Provide text details about the strain
3. Ask if they want to order

Example conversation:
```
Customer: "Tell me about Capjunky"
Bot: [Sends capjunky.jpg image]
     "Capjunky 🌿
     ราคา: 450฿ ต่อ 10 กรัม
     THC: 28%
     ประเภท: Hybrid

     Relaxing hybrid with sweet, earthy flavors

     อยากสั่งไหมคะ?"
```

## Deployment

### Option 1: Host on External Service (Recommended for Railway)
1. Upload images to image hosting service (Imgur, Cloudinary, etc.)
2. Update `customer_config.json` with full URLs:
```json
"image": "https://i.imgur.com/YOUR_IMAGE.jpg"
```

### Option 2: Host Locally (For local development)
1. Place images in `product_images/` folder
2. Images will be served at `/images/{filename}`

## Current Product List

1. **Capjunky** - Hybrid, 28% THC
2. **Alien Marker** - Indica, 26% THC
3. **Trop Cherry** - Hybrid, 27% THC
4. **Gogurtz** - Hybrid, 29% THC
5. **Berry Bonds** - Indica, 25% THC
6. **LCG x Grapegas** - Hybrid, 30% THC
7. **Apple Banana** - Sativa, 24% THC

All priced at 450฿ per 10 grams.
