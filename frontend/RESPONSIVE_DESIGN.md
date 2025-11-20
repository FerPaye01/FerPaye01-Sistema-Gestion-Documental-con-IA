# Diseño Responsivo - SGD UGEL Ilo

## Breakpoints de TailwindCSS

El sistema utiliza los siguientes breakpoints para diseño responsivo:

| Breakpoint | Tamaño Mínimo | Dispositivo Objetivo |
|------------|---------------|---------------------|
| `xs`       | 475px         | Móviles grandes     |
| `sm`       | 640px         | Tablets pequeñas    |
| `md`       | 768px         | Tablets             |
| `lg`       | 1024px        | Laptops             |
| `xl`       | 1280px        | Desktops            |
| `2xl`      | 1536px        | Pantallas grandes   |

## Estrategias de Optimización

### 1. Lazy Loading de Componentes

Los componentes pesados se cargan de forma diferida usando `React.lazy()`:

```typescript
const UploadComponent = lazy(() => import('./components/UploadComponent'));
const SearchComponent = lazy(() => import('./components/SearchComponent'));
const DocumentViewer = lazy(() => import('./components/DocumentViewer'));
```

**Beneficios:**
- Reduce el tamaño del bundle inicial
- Mejora el tiempo de carga inicial (First Contentful Paint)
- Los componentes se cargan solo cuando son necesarios

### 2. Preload de Recursos Críticos

En `index.html` se precargan recursos críticos:

```html
<!-- Preconnect to API -->
<link rel="preconnect" href="/api" />

<!-- Preload PDF.js worker -->
<link rel="preload" href="//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js" as="script" />
```

### 3. Lazy Loading de Imágenes

El componente `LazyImage` utiliza Intersection Observer para cargar imágenes solo cuando están cerca del viewport:

```typescript
import LazyImage from './components/LazyImage';

<LazyImage 
  src={documento.thumbnail_url} 
  alt={documento.filename}
  className="w-full h-auto"
/>
```

### 4. Hooks Personalizados para Responsive Design

```typescript
import { useIsMobile, useIsTablet, useIsDesktop } from './hooks/useMediaQuery';

function MyComponent() {
  const isMobile = useIsMobile();
  const isTablet = useIsTablet();
  const isDesktop = useIsDesktop();
  
  return (
    <div>
      {isMobile && <MobileLayout />}
      {isTablet && <TabletLayout />}
      {isDesktop && <DesktopLayout />}
    </div>
  );
}
```

## Componentes Responsivos

### UploadComponent

**Móvil (< 768px):**
- Zona de drop simplificada
- Botones apilados verticalmente
- Texto reducido

**Tablet (768px - 1023px):**
- Zona de drop de tamaño medio
- Botones en fila
- Información completa

**Desktop (≥ 1024px):**
- Zona de drop amplia
- Layout horizontal optimizado
- Información detallada con iconos

### SearchComponent

**Móvil:**
- Filtros colapsables
- Resultados en lista vertical
- 1 columna de filtros

**Tablet:**
- Filtros visibles
- 2 columnas de filtros
- Resultados con más detalles

**Desktop:**
- 3 columnas de filtros
- Resultados con información completa
- Paginación expandida

### DocumentViewer

**Móvil:**
- Controles simplificados
- Zoom táctil nativo
- Botones grandes para touch

**Tablet:**
- Controles completos
- Toolbar en una fila
- Navegación optimizada

**Desktop:**
- Todos los controles visibles
- Atajos de teclado
- Vista previa de páginas

## Optimizaciones de Rendimiento

### Code Splitting

Vite automáticamente divide el código en chunks:

```
dist/
├── assets/
│   ├── index-[hash].js          # Bundle principal
│   ├── UploadComponent-[hash].js
│   ├── SearchComponent-[hash].js
│   └── DocumentViewer-[hash].js
```

### Tree Shaking

Solo se incluyen las partes de las bibliotecas que realmente se usan:

- TailwindCSS: Solo las clases utilizadas
- react-pdf: Solo los componentes necesarios
- axios: Configuración mínima

### Compresión

En producción, Vite genera:
- Archivos minificados
- Gzip/Brotli compression
- Source maps separados

## Testing Responsivo

### Herramientas Recomendadas

1. **Chrome DevTools**
   - Device Mode para simular dispositivos
   - Network throttling para conexiones lentas

2. **Responsive Design Mode (Firefox)**
   - Múltiples viewports simultáneos
   - Touch simulation

3. **BrowserStack / LambdaTest**
   - Testing en dispositivos reales
   - Múltiples navegadores y versiones

### Checklist de Testing

- [ ] Navegación funciona en móvil
- [ ] Formularios son usables en touch
- [ ] Imágenes se cargan correctamente
- [ ] Texto es legible sin zoom
- [ ] Botones tienen tamaño mínimo de 44x44px
- [ ] No hay scroll horizontal
- [ ] Modales se adaptan al viewport
- [ ] Performance es aceptable en 3G

## Mejores Prácticas

### 1. Mobile-First Approach

Escribir estilos base para móvil y usar breakpoints para pantallas más grandes:

```tsx
<div className="text-sm sm:text-base md:text-lg">
  Texto responsivo
</div>
```

### 2. Touch-Friendly

Asegurar que elementos interactivos sean fáciles de tocar:

```tsx
<button className="min-h-[44px] min-w-[44px] p-3">
  Botón táctil
</button>
```

### 3. Contenido Adaptativo

Mostrar/ocultar contenido según el dispositivo:

```tsx
<span className="hidden sm:inline">Texto completo</span>
<span className="sm:hidden">Texto corto</span>
```

### 4. Imágenes Responsivas

Usar diferentes tamaños de imagen según el dispositivo:

```tsx
<img 
  srcSet="image-small.jpg 480w, image-medium.jpg 768w, image-large.jpg 1200w"
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  src="image-medium.jpg"
  alt="Descripción"
/>
```

## Métricas de Rendimiento

### Objetivos

- **First Contentful Paint (FCP):** < 1.8s
- **Largest Contentful Paint (LCP):** < 2.5s
- **Time to Interactive (TTI):** < 3.8s
- **Cumulative Layout Shift (CLS):** < 0.1
- **First Input Delay (FID):** < 100ms

### Monitoreo

Usar Lighthouse para auditorías regulares:

```bash
npm run build
npx lighthouse http://localhost:3000 --view
```

## Recursos Adicionales

- [TailwindCSS Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [Web.dev - Responsive Images](https://web.dev/responsive-images/)
- [MDN - Responsive Design](https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design)
- [React Performance Optimization](https://react.dev/learn/render-and-commit#optimizing-performance)
