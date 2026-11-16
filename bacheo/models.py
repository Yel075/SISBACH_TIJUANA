from django.db import models


class Bache(models.Model):

    GRAVEDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Critica', 'Critica')
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Reparado', 'Reparado')
    ]

    ubicacion = models.CharField(max_length=255)
    latitud = models.FloatField()
    longitud = models.FloatField()
    direccion = models.CharField(max_length=250, blank=True, null=True)
    
    def __str__(self):
            return self.ubicacion

    def calcularPrioridad(self):
    
         prioridades = {
            'Baja': 10,
            'Media': 30,
            'Alta': 60,
            'Critica': 80
        }
         prioridad_base = prioridades.get(self.gravedad, 0)
         bonus_reportes = min(50, self.reportes.count() * 10)
    
         return prioridad_base + bonus_reportes

    gravedad = models.CharField(
        max_length=20,
        choices=GRAVEDAD_CHOICES,
        default='Media'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Pendiente'
    )

    diametro_cm = models.FloatField(default=0)
    profundidad_cm = models.FloatField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_reparacion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ubicacion

class Reporte(models.Model):
    bache = models.ForeignKey(
        Bache,
        on_delete=models.CASCADE,
        related_name='reportes'
    )

    ciudadano_nombre = models.CharField(
        max_length=120
    )

    comentario = models.TextField()

    foto= models.ImageField(
     upload_to='reportes/',
     null=True,
     blank=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.ciudadano_nombre

    direccion = models.CharField(
    max_length=300,
    blank=True,
    default=""
    )

    
