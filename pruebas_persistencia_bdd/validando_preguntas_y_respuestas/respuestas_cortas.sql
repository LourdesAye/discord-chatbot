SELECT *
FROM respuestas
WHERE LENGTH(TRIM(texto)) <= 10;  -- o ajustá el límite
-- 85 respuestas

