SELECT SUM(conteo - 1)
FROM (
    SELECT COUNT(*) AS conteo
    FROM mensajes
    GROUP BY contenido
    HAVING COUNT(*) > 1
) sub;
