PGDMP  :                    }            base_de_conocimiento_chatbot    17.4    17.4 <    g           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                           false            h           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                           false            i           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                           false            j           1262    24576    base_de_conocimiento_chatbot    DATABASE     �   CREATE DATABASE base_de_conocimiento_chatbot WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'es-AR';
 ,   DROP DATABASE base_de_conocimiento_chatbot;
                     postgres    false            �            1259    34450    adjuntos    TABLE     �   CREATE TABLE public.adjuntos (
    id_adjunto integer NOT NULL,
    mensaje_id integer NOT NULL,
    url text NOT NULL,
    tipo text
);
    DROP TABLE public.adjuntos;
       public         heap r       postgres    false            �            1259    34449    adjuntos_id_adjunto_seq    SEQUENCE     �   CREATE SEQUENCE public.adjuntos_id_adjunto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.adjuntos_id_adjunto_seq;
       public               postgres    false    222            k           0    0    adjuntos_id_adjunto_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.adjuntos_id_adjunto_seq OWNED BY public.adjuntos.id_adjunto;
          public               postgres    false    221            �            1259    34426    autores    TABLE     �   CREATE TABLE public.autores (
    id_autor integer NOT NULL,
    nombre_autor text NOT NULL,
    es_docente boolean NOT NULL
);
    DROP TABLE public.autores;
       public         heap r       postgres    false            �            1259    34425    autores_id_autor_seq    SEQUENCE     �   CREATE SEQUENCE public.autores_id_autor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 +   DROP SEQUENCE public.autores_id_autor_seq;
       public               postgres    false    218            l           0    0    autores_id_autor_seq    SEQUENCE OWNED BY     M   ALTER SEQUENCE public.autores_id_autor_seq OWNED BY public.autores.id_autor;
          public               postgres    false    217            �            1259    34516 
   embeddings    TABLE     �   CREATE TABLE public.embeddings (
    id_embedding integer NOT NULL,
    fragmento_id integer NOT NULL,
    id_chroma_db text NOT NULL
);
    DROP TABLE public.embeddings;
       public         heap r       postgres    false            �            1259    34515    embeddings_id_embedding_seq    SEQUENCE     �   CREATE SEQUENCE public.embeddings_id_embedding_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.embeddings_id_embedding_seq;
       public               postgres    false    230            m           0    0    embeddings_id_embedding_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.embeddings_id_embedding_seq OWNED BY public.embeddings.id_embedding;
          public               postgres    false    229            �            1259    34502    fragmentos_preguntas    TABLE     �   CREATE TABLE public.fragmentos_preguntas (
    id_fragmento integer NOT NULL,
    pregunta_id integer NOT NULL,
    texto_fragmento text NOT NULL,
    orden integer NOT NULL
);
 (   DROP TABLE public.fragmentos_preguntas;
       public         heap r       postgres    false            �            1259    34501 %   fragmentos_preguntas_id_fragmento_seq    SEQUENCE     �   CREATE SEQUENCE public.fragmentos_preguntas_id_fragmento_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 <   DROP SEQUENCE public.fragmentos_preguntas_id_fragmento_seq;
       public               postgres    false    228            n           0    0 %   fragmentos_preguntas_id_fragmento_seq    SEQUENCE OWNED BY     o   ALTER SEQUENCE public.fragmentos_preguntas_id_fragmento_seq OWNED BY public.fragmentos_preguntas.id_fragmento;
          public               postgres    false    227            �            1259    34435    mensajes    TABLE       CREATE TABLE public.mensajes (
    id_mensaje integer NOT NULL,
    id_mensaje_discord bigint NOT NULL,
    autor_id integer NOT NULL,
    fecha_mensaje timestamp without time zone NOT NULL,
    contenido text NOT NULL,
    es_pregunta boolean DEFAULT false,
    origen text
);
    DROP TABLE public.mensajes;
       public         heap r       postgres    false            �            1259    34434    mensajes_id_mensaje_seq    SEQUENCE     �   CREATE SEQUENCE public.mensajes_id_mensaje_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.mensajes_id_mensaje_seq;
       public               postgres    false    220            o           0    0    mensajes_id_mensaje_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.mensajes_id_mensaje_seq OWNED BY public.mensajes.id_mensaje;
          public               postgres    false    219            �            1259    34464 	   preguntas    TABLE     �   CREATE TABLE public.preguntas (
    id_pregunta integer NOT NULL,
    mensaje_id integer NOT NULL,
    texto text NOT NULL,
    esta_cerrada boolean DEFAULT false,
    sin_contexto boolean DEFAULT false,
    es_administrativa boolean DEFAULT false
);
    DROP TABLE public.preguntas;
       public         heap r       postgres    false            �            1259    34463    preguntas_id_pregunta_seq    SEQUENCE     �   CREATE SEQUENCE public.preguntas_id_pregunta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 0   DROP SEQUENCE public.preguntas_id_pregunta_seq;
       public               postgres    false    224            p           0    0    preguntas_id_pregunta_seq    SEQUENCE OWNED BY     W   ALTER SEQUENCE public.preguntas_id_pregunta_seq OWNED BY public.preguntas.id_pregunta;
          public               postgres    false    223            �            1259    34481 
   respuestas    TABLE        CREATE TABLE public.respuestas (
    id_respuesta integer NOT NULL,
    mensaje_id integer NOT NULL,
    pregunta_id integer NOT NULL,
    texto text NOT NULL,
    orden integer,
    es_validada boolean DEFAULT false,
    es_corta boolean DEFAULT false
);
    DROP TABLE public.respuestas;
       public         heap r       postgres    false            �            1259    34480    respuestas_id_respuesta_seq    SEQUENCE     �   CREATE SEQUENCE public.respuestas_id_respuesta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.respuestas_id_respuesta_seq;
       public               postgres    false    226            q           0    0    respuestas_id_respuesta_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.respuestas_id_respuesta_seq OWNED BY public.respuestas.id_respuesta;
          public               postgres    false    225            �           2604    34453    adjuntos id_adjunto    DEFAULT     z   ALTER TABLE ONLY public.adjuntos ALTER COLUMN id_adjunto SET DEFAULT nextval('public.adjuntos_id_adjunto_seq'::regclass);
 B   ALTER TABLE public.adjuntos ALTER COLUMN id_adjunto DROP DEFAULT;
       public               postgres    false    221    222    222            �           2604    34429    autores id_autor    DEFAULT     t   ALTER TABLE ONLY public.autores ALTER COLUMN id_autor SET DEFAULT nextval('public.autores_id_autor_seq'::regclass);
 ?   ALTER TABLE public.autores ALTER COLUMN id_autor DROP DEFAULT;
       public               postgres    false    218    217    218            �           2604    34519    embeddings id_embedding    DEFAULT     �   ALTER TABLE ONLY public.embeddings ALTER COLUMN id_embedding SET DEFAULT nextval('public.embeddings_id_embedding_seq'::regclass);
 F   ALTER TABLE public.embeddings ALTER COLUMN id_embedding DROP DEFAULT;
       public               postgres    false    229    230    230            �           2604    34505 !   fragmentos_preguntas id_fragmento    DEFAULT     �   ALTER TABLE ONLY public.fragmentos_preguntas ALTER COLUMN id_fragmento SET DEFAULT nextval('public.fragmentos_preguntas_id_fragmento_seq'::regclass);
 P   ALTER TABLE public.fragmentos_preguntas ALTER COLUMN id_fragmento DROP DEFAULT;
       public               postgres    false    227    228    228            �           2604    34438    mensajes id_mensaje    DEFAULT     z   ALTER TABLE ONLY public.mensajes ALTER COLUMN id_mensaje SET DEFAULT nextval('public.mensajes_id_mensaje_seq'::regclass);
 B   ALTER TABLE public.mensajes ALTER COLUMN id_mensaje DROP DEFAULT;
       public               postgres    false    220    219    220            �           2604    34467    preguntas id_pregunta    DEFAULT     ~   ALTER TABLE ONLY public.preguntas ALTER COLUMN id_pregunta SET DEFAULT nextval('public.preguntas_id_pregunta_seq'::regclass);
 D   ALTER TABLE public.preguntas ALTER COLUMN id_pregunta DROP DEFAULT;
       public               postgres    false    224    223    224            �           2604    34484    respuestas id_respuesta    DEFAULT     �   ALTER TABLE ONLY public.respuestas ALTER COLUMN id_respuesta SET DEFAULT nextval('public.respuestas_id_respuesta_seq'::regclass);
 F   ALTER TABLE public.respuestas ALTER COLUMN id_respuesta DROP DEFAULT;
       public               postgres    false    226    225    226            \          0    34450    adjuntos 
   TABLE DATA           E   COPY public.adjuntos (id_adjunto, mensaje_id, url, tipo) FROM stdin;
    public               postgres    false    222   �J       X          0    34426    autores 
   TABLE DATA           E   COPY public.autores (id_autor, nombre_autor, es_docente) FROM stdin;
    public               postgres    false    218    K       d          0    34516 
   embeddings 
   TABLE DATA           N   COPY public.embeddings (id_embedding, fragmento_id, id_chroma_db) FROM stdin;
    public               postgres    false    230   �K       b          0    34502    fragmentos_preguntas 
   TABLE DATA           a   COPY public.fragmentos_preguntas (id_fragmento, pregunta_id, texto_fragmento, orden) FROM stdin;
    public               postgres    false    228   �K       Z          0    34435    mensajes 
   TABLE DATA           {   COPY public.mensajes (id_mensaje, id_mensaje_discord, autor_id, fecha_mensaje, contenido, es_pregunta, origen) FROM stdin;
    public               postgres    false    220   �K       ^          0    34464 	   preguntas 
   TABLE DATA           r   COPY public.preguntas (id_pregunta, mensaje_id, texto, esta_cerrada, sin_contexto, es_administrativa) FROM stdin;
    public               postgres    false    224   �K       `          0    34481 
   respuestas 
   TABLE DATA           p   COPY public.respuestas (id_respuesta, mensaje_id, pregunta_id, texto, orden, es_validada, es_corta) FROM stdin;
    public               postgres    false    226    L       r           0    0    adjuntos_id_adjunto_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.adjuntos_id_adjunto_seq', 1, false);
          public               postgres    false    221            s           0    0    autores_id_autor_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.autores_id_autor_seq', 8, true);
          public               postgres    false    217            t           0    0    embeddings_id_embedding_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.embeddings_id_embedding_seq', 1, false);
          public               postgres    false    229            u           0    0 %   fragmentos_preguntas_id_fragmento_seq    SEQUENCE SET     T   SELECT pg_catalog.setval('public.fragmentos_preguntas_id_fragmento_seq', 1, false);
          public               postgres    false    227            v           0    0    mensajes_id_mensaje_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.mensajes_id_mensaje_seq', 1, false);
          public               postgres    false    219            w           0    0    preguntas_id_pregunta_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.preguntas_id_pregunta_seq', 1, false);
          public               postgres    false    223            x           0    0    respuestas_id_respuesta_seq    SEQUENCE SET     J   SELECT pg_catalog.setval('public.respuestas_id_respuesta_seq', 1, false);
          public               postgres    false    225            �           2606    34457    adjuntos adjuntos_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.adjuntos
    ADD CONSTRAINT adjuntos_pkey PRIMARY KEY (id_adjunto);
 @   ALTER TABLE ONLY public.adjuntos DROP CONSTRAINT adjuntos_pkey;
       public                 postgres    false    222            �           2606    34433    autores autores_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.autores
    ADD CONSTRAINT autores_pkey PRIMARY KEY (id_autor);
 >   ALTER TABLE ONLY public.autores DROP CONSTRAINT autores_pkey;
       public                 postgres    false    218            �           2606    34523    embeddings embeddings_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.embeddings
    ADD CONSTRAINT embeddings_pkey PRIMARY KEY (id_embedding);
 D   ALTER TABLE ONLY public.embeddings DROP CONSTRAINT embeddings_pkey;
       public                 postgres    false    230            �           2606    34509 .   fragmentos_preguntas fragmentos_preguntas_pkey 
   CONSTRAINT     v   ALTER TABLE ONLY public.fragmentos_preguntas
    ADD CONSTRAINT fragmentos_preguntas_pkey PRIMARY KEY (id_fragmento);
 X   ALTER TABLE ONLY public.fragmentos_preguntas DROP CONSTRAINT fragmentos_preguntas_pkey;
       public                 postgres    false    228            �           2606    34443    mensajes mensajes_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.mensajes
    ADD CONSTRAINT mensajes_pkey PRIMARY KEY (id_mensaje);
 @   ALTER TABLE ONLY public.mensajes DROP CONSTRAINT mensajes_pkey;
       public                 postgres    false    220            �           2606    34474    preguntas preguntas_pkey 
   CONSTRAINT     _   ALTER TABLE ONLY public.preguntas
    ADD CONSTRAINT preguntas_pkey PRIMARY KEY (id_pregunta);
 B   ALTER TABLE ONLY public.preguntas DROP CONSTRAINT preguntas_pkey;
       public                 postgres    false    224            �           2606    34490    respuestas respuestas_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.respuestas
    ADD CONSTRAINT respuestas_pkey PRIMARY KEY (id_respuesta);
 D   ALTER TABLE ONLY public.respuestas DROP CONSTRAINT respuestas_pkey;
       public                 postgres    false    226            �           2606    34458 !   adjuntos adjuntos_mensaje_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.adjuntos
    ADD CONSTRAINT adjuntos_mensaje_id_fkey FOREIGN KEY (mensaje_id) REFERENCES public.mensajes(id_mensaje) ON DELETE CASCADE;
 K   ALTER TABLE ONLY public.adjuntos DROP CONSTRAINT adjuntos_mensaje_id_fkey;
       public               postgres    false    222    220    4788            �           2606    34524 '   embeddings embeddings_fragmento_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.embeddings
    ADD CONSTRAINT embeddings_fragmento_id_fkey FOREIGN KEY (fragmento_id) REFERENCES public.fragmentos_preguntas(id_fragmento) ON DELETE CASCADE;
 Q   ALTER TABLE ONLY public.embeddings DROP CONSTRAINT embeddings_fragmento_id_fkey;
       public               postgres    false    230    4796    228            �           2606    34510 :   fragmentos_preguntas fragmentos_preguntas_pregunta_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.fragmentos_preguntas
    ADD CONSTRAINT fragmentos_preguntas_pregunta_id_fkey FOREIGN KEY (pregunta_id) REFERENCES public.preguntas(id_pregunta) ON DELETE CASCADE;
 d   ALTER TABLE ONLY public.fragmentos_preguntas DROP CONSTRAINT fragmentos_preguntas_pregunta_id_fkey;
       public               postgres    false    228    4792    224            �           2606    34444    mensajes mensajes_autor_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.mensajes
    ADD CONSTRAINT mensajes_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES public.autores(id_autor) ON DELETE CASCADE;
 I   ALTER TABLE ONLY public.mensajes DROP CONSTRAINT mensajes_autor_id_fkey;
       public               postgres    false    218    220    4786            �           2606    34475 #   preguntas preguntas_mensaje_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.preguntas
    ADD CONSTRAINT preguntas_mensaje_id_fkey FOREIGN KEY (mensaje_id) REFERENCES public.mensajes(id_mensaje) ON DELETE CASCADE;
 M   ALTER TABLE ONLY public.preguntas DROP CONSTRAINT preguntas_mensaje_id_fkey;
       public               postgres    false    220    224    4788            �           2606    34491 %   respuestas respuestas_mensaje_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.respuestas
    ADD CONSTRAINT respuestas_mensaje_id_fkey FOREIGN KEY (mensaje_id) REFERENCES public.mensajes(id_mensaje) ON DELETE CASCADE;
 O   ALTER TABLE ONLY public.respuestas DROP CONSTRAINT respuestas_mensaje_id_fkey;
       public               postgres    false    226    4788    220            �           2606    34496 &   respuestas respuestas_pregunta_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.respuestas
    ADD CONSTRAINT respuestas_pregunta_id_fkey FOREIGN KEY (pregunta_id) REFERENCES public.preguntas(id_pregunta) ON DELETE CASCADE;
 P   ALTER TABLE ONLY public.respuestas DROP CONSTRAINT respuestas_pregunta_id_fkey;
       public               postgres    false    226    4792    224            \      x������ � �      X   |   x��Q�0���1�(�]L�kY�I�ꖚ��]���d:�/�[�\����9O�3˳B��A6�Sn�"����LĶ�*+��̅t�t�6��p8��%SW�˖ȁ��#	�Z�Pt�����v18      d      x������ � �      b      x������ � �      Z      x������ � �      ^      x������ � �      `      x������ � �     