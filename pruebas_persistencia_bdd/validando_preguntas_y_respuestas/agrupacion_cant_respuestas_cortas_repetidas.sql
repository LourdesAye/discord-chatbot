SELECT r.texto, count(*)
FROM respuestas r
WHERE LENGTH(TRIM(texto)) <= 10  -- o ajustá el límite
group by r.texto
order by count(*) desc
