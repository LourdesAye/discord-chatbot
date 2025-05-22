-- contenido repetido en mensajes
SELECT 
  contenido,
  COUNT(*) AS cantidad
FROM mensajes
GROUP BY contenido
HAVING COUNT(*) > 1
ORDER BY cantidad DESC;


