-- contenido repetido en mensajes
-- por cada mensaje cuántas veces aparece en la base de datos
SELECT 
  contenido,
  COUNT(*) AS cantidad
FROM mensajes
GROUP BY contenido
HAVING COUNT(*) > 1
ORDER BY cantidad DESC;


