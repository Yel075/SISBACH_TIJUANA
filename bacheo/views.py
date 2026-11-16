from django.shortcuts import render, redirect
from .models import Bache, Reporte
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from math import radians, sin, cos, sqrt, atan2

import urllib.request
import urllib.parse
import json

def obtener_direccion(latitud, longitud):

    try:

        url = (
            f"https://nominatim.openstreetmap.org/reverse"
            f"?format=json"
            f"&lat={latitud}"
            f"&lon={longitud}"
        )

        headers = {
            "User-Agent": "SISBACH-TIJ"
        }

        req = urllib.request.Request(
            url,
            headers=headers
        )

        with urllib.request.urlopen(
            req,
            timeout=5
        ) as response:

            data = json.loads(
                response.read().decode()
            )

            return data.get(
                "display_name",
                "Dirección no encontrada"
            )

    except:

        return f"Lat: {latitud}, Lon: {longitud}"

def distancia_metros(lat1, lon1, lat2, lon2):

    R = 6371000

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2 +
        cos(radians(lat1)) *
        cos(radians(lat2)) *
        sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


def inicio(request):

    if request.method == 'POST':
        print("FORMULARIO ENVIADO")
        ciudadano_nombre = request.POST ['ciudadano_nombre']
        comentario = request.POST ['comentario']
        ubicacion = request.POST ['ubicacion']
        gravedad = request.POST ['gravedad']
        estado = request.POST ['estado']
        latitud = request.POST.get("latitud",0)
        longitud = request.POST.get("longitud",0)
        direccion = obtener_direccion(latitud, longitud)
        print("DIRECCION OBTENIDA:", direccion)
        bache_existente = None

        for bache in Bache.objects.filter(estado='Pendiente'):

              distancia = distancia_metros(
              float(latitud),
              float(longitud),
              bache.latitud,
              bache.longitud
              )

              if distancia <= 20: 
                 bache_existente = bache 
                 break

        foto = request.FILES.get('foto')

        if bache_existente:
          niveles = {
             "Baja": 1,
             "Media": 2,
             "Alta": 3,
             "Critica": 4
            }
          if not bache_existente.direccion:
              bache_existente.direccion = direccion
              bache_existente.save()

          if niveles[gravedad] > niveles[bache_existente.gravedad]:
             bache_existente.gravedad = gravedad
             bache_existente.save()
 
          Reporte.objects.create(
             bache=bache_existente,
             ciudadano_nombre=ciudadano_nombre,
             comentario=comentario,
             foto=foto
            )
          return render(request,'bacheo/comprobante.html',{'bache': bache_existente})
        else:

         bache = Bache.objects.create(
             ubicacion=ubicacion,
             gravedad=gravedad,
             estado=estado,
             latitud=float(latitud),
             longitud=float(longitud),
             direccion=direccion,
             diametro_cm=0,
             profundidad_cm=0,
            )

         Reporte.objects.create(
              bache=bache,
              ciudadano_nombre=ciudadano_nombre,
              comentario=comentario,
              foto=foto
            )

         return render(request, 'bacheo/comprobante.html', {'bache':bache})
    
    baches = Bache.objects.filter(estado='Pendiente').order_by('-id')
    baches_reparados = Bache.objects.filter(estado='Reparado').order_by('-id')
    buscar = request.GET.get('buscar', '')
    cantidad_resultados = 0
    if buscar:
          baches = baches.filter(
          Q(ubicacion__icontains=buscar) |
          Q(gravedad__icontains=buscar) |
          Q(estado__icontains=buscar)
        )
          baches_reparados = baches_reparados.filter(
          Q(ubicacion__icontains=buscar) |
          Q(gravedad__icontains=buscar) |
          Q(estado__icontains=buscar)
        ) 
          cantidad_resultados = (
          baches.count() +
          baches_reparados.count()
        )
     
    
    for bache in baches: 
        bache.prioridad = bache.calcularPrioridad()
    for bache in baches_reparados:
        bache.prioridad = bache.calcularPrioridad()
    
    cima = max(baches, key=lambda b: b.calcularPrioridad(), default= None)
    total_baches = baches.count()
    total_pendientes = baches.count()
    total_reparados = baches_reparados.count()
    total_reportes = Reporte.objects.count()

    baches = baches[:10]
    baches_reparados = baches_reparados[:10]

    return render(
    request,
    'bacheo/index.html',
    {
        'baches': baches,
        'baches_reparados': baches_reparados,
        'total_baches': total_baches,
        'cima': cima,
        'total_pendientes': total_pendientes,
        'total_reparados': total_reparados,
        'total_reportes':total_reportes,
        'buscar': buscar,
        'cantidad_resultados': cantidad_resultados,
    }
    ) 

def atender_bache(request):
    print("POP EJECUTADO")
    baches_pendientes = Bache.objects.filter(estado = 'Pendiente')
    bache = max(baches_pendientes, key= lambda b: b.calcularPrioridad(), default= None)
    
    if bache: 
        print("SE VA A REPARAR:",
        bache.id,
        bache.gravedad,
        bache.calcularPrioridad()
        )
        bache.estado = 'Reparado'
        bache.fecha_reparacion = timezone.now()
        bache.save()

    return redirect('/')

def historial(request):
    lista_baches = Bache.objects.all().order_by('-id')
    paginator = Paginator(lista_baches, 10)
    page_number = request.GET.get('page')
    baches = paginator.get_page(page_number)
    return render(
        request,
        'bacheo/historial.html',{'baches': baches}
    )
