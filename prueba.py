# Este es solo un ejemplo de código para ilustrar el uso de atributos no públicos en Python.
# porque podriaa generar confusión el uso de atributos no públicos con getters y setters.
# En Python, los atributos no públicos se indican con un guion bajo (_) al inicio del nombre del atributo.
# Sin embargo, Python no tiene modificadores de acceso como otros lenguajes (por ejemplo, private, protected, public).
# Los atributos con un guion bajo son una convención que indica que no deben ser accedidos directamente desde fuera de la clase,
# pero aún son accesibles si se desea.
# A continuación, se muestra un ejemplo simple:
class Point:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def get_x(self):
        return self._x

    def set_x(self, value):
        self._x = value

    def get_y(self):
        return self._y

    def set_y(self, value):
        self._y = value

point = Point(12, 5)
result_1 = point.get_x()
result_2 = point.get_y()
result_3 = point.set_x(42)
result_4 = point.get_x()

# Non-public attributes are still accessible
result_5=point._x
result_6=point._y

for i in range(1,7,1):
    print(f"result_{i}: {eval('result_'+str(i))}")  

print("")

# Aunque el ejemplo que acaba de ver usa el estilo de codificación de Python, no es Pythonic. 
# En el ejemplo, los métodos getter y setter no realizan ningún procesamiento adicional 
# con los valores de ._x y ._y, por lo que podría tener atributos simples en lugar de métodos.

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


point = Point(12, 5)
result_x = point.x
result_y = point.y
point.x = 42
result_z= point.x

for i, res in enumerate([result_x, result_y, result_z], start=1):
    print(f"result_{i}: {res}")
print("")


# Ejemplo muestra cómo crear una clase Circle con una propiedad que administra su radio
class Circle:
    def __init__(self, radius):
        self._radius = radius # atributo no público

    def _get_radius(self): # getter
        print("Get radius")
        return self._radius

    def _set_radius(self, value): # setter
        print("Set radius")
        self._radius = value

    def _del_radius(self): # deleter
        print("Delete radius")
        del self._radius

    radius = property( # definición de la propiedad
        fget=_get_radius,
        fset=_set_radius,
        fdel=_del_radius,
        doc="The radius property."
    )

    