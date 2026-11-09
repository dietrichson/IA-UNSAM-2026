# 🍔 Burger Runner

Un runner 3D en el que una hamburguesa con patitas corre por 3 carriles,
esquiva obstáculos, junta monedas y activa un super salto al juntar
mayonesa + tomate + queso.

## Cómo correrlo
1. Abrir `index.html` en un navegador moderno (Chrome, Firefox, Safari).
2. O servirlo con: `python3 -m http.server 8000` y abrir `localhost:8000`.

## Controles
- ← / A: carril izquierdo
- → / D: carril derecho
- ↑ / W / Espacio: saltar
- Espacio (en game over): reintentar
- En móvil: swipe izquierda/derecha/arriba

## Niveles
- **Fácil:** 300 m, obstáculos separados
- **Medio:** 450 m, más obstáculos, más velocidad
- **Difícil:** 600 m, obstáculos juntos y meta lejana

## Power-up
Juntar los 3 ingredientes (mayonesa, tomate, queso) activa el super salto
por un único salto: sube el doble y permite alcanzar las bolsas de monedas
que flotan alto.

## Estructura