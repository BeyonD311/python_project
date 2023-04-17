--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dep_graph; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.dep_graph (
    parent_id integer,
    child_id integer
);


ALTER TABLE public.dep_graph OWNER TO project;

--
-- Name: departments; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(30),
    parent_department_id integer,
    is_active boolean,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    is_parent boolean DEFAULT false
);


ALTER TABLE public.departments OWNER TO project;

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.departments_id_seq OWNER TO project;

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: groups; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.groups (
    id smallint NOT NULL,
    name character varying(40)
);


ALTER TABLE public.groups OWNER TO project;

--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.groups_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.groups_id_seq OWNER TO project;

--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: head_of_departments; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.head_of_departments (
    id bigint NOT NULL,
    department_id integer,
    head_of_department_id bigint,
    deputy_head_id bigint,
    is_active boolean,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.head_of_departments OWNER TO project;

--
-- Name: head_of_depatments_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.head_of_depatments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.head_of_depatments_id_seq OWNER TO project;

--
-- Name: head_of_depatments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.head_of_depatments_id_seq OWNED BY public.head_of_departments.id;


--
-- Name: images; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.images (
    id bigint NOT NULL,
    path character varying
);


ALTER TABLE public.images OWNER TO project;

--
-- Name: images_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.images_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.images_id_seq OWNER TO project;

--
-- Name: images_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.images_id_seq OWNED BY public.images.id;


--
-- Name: inner_phones; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.inner_phones (
    id bigint NOT NULL,
    uuid character varying,
    user_id bigint,
    phone_number bigint,
    description text,
    is_registration boolean,
    is_default boolean,
    login character varying NOT NULL,
    password character varying NOT NULL,
    duration_call time without time zone,
    duration_conversation time without time zone,
    incoming_calls smallint,
    comment text
);


ALTER TABLE public.inner_phones OWNER TO project;

--
-- Name: inner_phones_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.inner_phones_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.inner_phones_id_seq OWNER TO project;

--
-- Name: inner_phones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.inner_phones_id_seq OWNED BY public.inner_phones.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.permissions (
    id smallint NOT NULL,
    module_name character varying(40),
    name character varying(40)
);


ALTER TABLE public.permissions OWNER TO project;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.permissions_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.permissions_id_seq OWNER TO project;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: position; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public."position" (
    id smallint NOT NULL,
    name character varying(40)
);


ALTER TABLE public."position" OWNER TO project;

--
-- Name: position_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.position_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.position_id_seq OWNER TO project;

--
-- Name: position_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.position_id_seq OWNED BY public."position".id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.roles (
    id smallint NOT NULL,
    name character varying(40),
    is_active boolean
);


ALTER TABLE public.roles OWNER TO project;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.roles_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO project;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: roles_permission; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.roles_permission (
    id bigint NOT NULL,
    role_id smallint NOT NULL,
    module_id smallint NOT NULL,
    is_active boolean,
    is_available boolean,
    method_access character varying(10)
);


ALTER TABLE public.roles_permission OWNER TO project;

--
-- Name: skills; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.skills (
    id bigint NOT NULL,
    name character varying
);


ALTER TABLE public.skills OWNER TO project;

--
-- Name: skills_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.skills_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.skills_id_seq OWNER TO project;

--
-- Name: skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.skills_id_seq OWNED BY public.skills.id;


--
-- Name: status_history; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.status_history (
    id bigint NOT NULL,
    user_id bigint,
    status_id smallint,
    update_at timestamp without time zone,
    time_at time without time zone,
    is_active boolean
);


ALTER TABLE public.status_history OWNER TO project;

--
-- Name: status_history_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.status_history_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.status_history_id_seq OWNER TO project;

--
-- Name: status_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.status_history_id_seq OWNED BY public.status_history.id;


--
-- Name: status_users; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.status_users (
    id smallint NOT NULL,
    name character varying,
    color character varying(20),
    code character varying(60),
    behavior character varying(60),
    alter_name character varying(60),
    life_time time without time zone
);


ALTER TABLE public.status_users OWNER TO project;

--
-- Name: status_users_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.status_users_id_seq
    AS smallint
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.status_users_id_seq OWNER TO project;

--
-- Name: status_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.status_users_id_seq OWNED BY public.status_users.id;


--
-- Name: user_groups; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.user_groups (
    user_id bigint NOT NULL,
    group_id smallint NOT NULL
);


ALTER TABLE public.user_groups OWNER TO project;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.user_roles (
    user_id bigint NOT NULL,
    role_id smallint NOT NULL
);


ALTER TABLE public.user_roles OWNER TO project;

--
-- Name: user_skills; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.user_skills (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL
);


ALTER TABLE public.user_skills OWNER TO project;

--
-- Name: users; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying,
    password character varying,
    name character varying NOT NULL,
    last_name character varying NOT NULL,
    patronymic character varying,
    fio character varying,
    login character varying NOT NULL,
    is_operator boolean,
    phone character varying(25),
    is_active boolean,
    photo_path character varying,
    position_id smallint,
    status_id integer,
    date_employment_at timestamp without time zone,
    date_dismissal_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    status_at timestamp without time zone,
    department_id integer,
    image_id bigint,
    personal_number character varying(30),
    employment_status boolean DEFAULT true,
    uuid character varying(100)
);


ALTER TABLE public.users OWNER TO project;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO project;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: users_permission; Type: TABLE; Schema: public; Owner: project
--

CREATE TABLE public.users_permission (
    id bigint NOT NULL,
    user_id bigint,
    role_id smallint,
    module_id smallint,
    is_active boolean,
    is_available boolean,
    method_access character varying(10)
);


ALTER TABLE public.users_permission OWNER TO project;

--
-- Name: users_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: project
--

CREATE SEQUENCE public.users_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_permission_id_seq OWNER TO project;

--
-- Name: users_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: project
--

ALTER SEQUENCE public.users_permission_id_seq OWNED BY public.users_permission.id;


--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: head_of_departments id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.head_of_departments ALTER COLUMN id SET DEFAULT nextval('public.head_of_depatments_id_seq'::regclass);


--
-- Name: images id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.images ALTER COLUMN id SET DEFAULT nextval('public.images_id_seq'::regclass);


--
-- Name: inner_phones id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.inner_phones ALTER COLUMN id SET DEFAULT nextval('public.inner_phones_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: position id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public."position" ALTER COLUMN id SET DEFAULT nextval('public.position_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: skills id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.skills ALTER COLUMN id SET DEFAULT nextval('public.skills_id_seq'::regclass);


--
-- Name: status_history id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.status_history ALTER COLUMN id SET DEFAULT nextval('public.status_history_id_seq'::regclass);


--
-- Name: status_users id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.status_users ALTER COLUMN id SET DEFAULT nextval('public.status_users_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: users_permission id; Type: DEFAULT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users_permission ALTER COLUMN id SET DEFAULT nextval('public.users_permission_id_seq'::regclass);


--
-- Data for Name: dep_graph; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.dep_graph (parent_id, child_id) FROM stdin;
1	6
1	7
2	6
2	7
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.departments (id, name, parent_department_id, is_active, created_at, updated_at, is_parent) FROM stdin;
1	Администрация	\N	t	2023-02-14 10:29:06.998784	2023-03-06 06:56:12.640463	f
3	Логистика	\N	t	2023-02-15 13:03:51.606856	2023-02-16 11:55:17.117074	f
7	Операторы	5	t	2023-02-15 13:05:43.168224	2023-02-15 13:05:43.168224	f
5	Колл-центр	\N	t	2023-02-15 13:05:51.978961	2023-02-16 07:16:03.913033	t
2	Отдел закупок	\N	t	2023-02-14 14:02:44.865458	2023-02-28 10:11:07.515402	f
4	Продажи	\N	t	2023-02-15 13:05:11.945845	2023-02-16 11:55:07.06845	f
6	string	\N	t	2023-02-15 13:05:29.306334	2023-03-31 12:13:11.258343	f
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.groups (id, name) FROM stdin;
1	Тестовая группа
2	Группа 2
\.


--
-- Data for Name: head_of_departments; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.head_of_departments (id, department_id, head_of_department_id, deputy_head_id, is_active, created_at) FROM stdin;
14	6	69	\N	t	2023-03-31 12:13:11.258343
21	6	\N	71	t	2023-03-31 13:19:55.903874
\.


--
-- Data for Name: images; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.images (id, path) FROM stdin;
1	/images/user_image/Снимок_экрана_(1).png
2	/images/user_image/Снимок_экрана_(3).png
3	/images/user_image/0798df584cbb20e2baf1f9f327f23f30.png
4	/images/user_image/a20443e1813384f52d18efdff0ba301d.png
5	/images/user_image/5f19824a5a31cd8df3681c5593a56850.png
6	/images/user_image/5f19824a5a31cd8df3681c5593a56850.png
\.


--
-- Data for Name: inner_phones; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.inner_phones (id, uuid, user_id, phone_number, description, is_registration, is_default, login, password, duration_call, duration_conversation, incoming_calls, comment) FROM stdin;
13	587ec7bb-f53d-4b66-8f74-f86e4617d951	69	1005	string	t	t	string	string	01:00:11	00:09:15	0	string
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.permissions (id, module_name, name) FROM stdin;
1	users	Управление пользователями
2	deparment	Отелы
3	roles	Роли
\.


--
-- Data for Name: position; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public."position" (id, name) FROM stdin;
1	Тестовая долность
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.roles (id, name, is_active) FROM stdin;
1	admin	t
3	Супервизор	t
2	string	t
\.


--
-- Data for Name: roles_permission; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.roles_permission (id, role_id, module_id, is_active, is_available, method_access) FROM stdin;
2	1	2	t	t	00000
3	1	3	t	t	00000
5	2	2	t	t	00000
6	2	3	t	t	00000
7	3	1	t	t	00000
8	3	2	t	t	00000
9	3	3	t	t	00000
1	1	1	t	t	01000
4	2	1	t	t	01000
\.


--
-- Data for Name: skills; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.skills (id, name) FROM stdin;
1	Работник
2	Пользователь
3	Тестовый
\.


--
-- Data for Name: status_history; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.status_history (id, user_id, status_id, update_at, time_at, is_active) FROM stdin;
136	69	10	2023-04-11 15:52:38	00:00:00	f
137	69	10	2023-04-11 15:52:38	\N	t
\.


--
-- Data for Name: status_users; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.status_users (id, name, color, code, behavior, alter_name, life_time) FROM stdin;
1	Предварительная обработка	\N	precall	\N	\N	\N
2	Ожидание ответа абонента	\N	callwaiting	\N	\N	\N
3	Обратный вызов	\N	callback	\N	\N	\N
4	Разговор с абонентом	\N	externalcall	\N	\N	\N
5	Разговор между операторами	\N	internalcall	\N	\N	\N
6	Разговор по задаче	\N	taskcall	\N	\N	\N
7	Поствызывная обработка	\N	aftercall	\N	\N	\N
8	Прочие разговоры	\N	othercall	\N	\N	\N
9	Перерыв	\N	break	\N	\N	\N
10	Готов	\N	ready	\N	\N	\N
11	Ручной режим коллцентра	\N	manualcallcenter	\N	\N	\N
12	Обратный вызов из текстовой задачи	\N	taskcallback	\N	\N	\N
13	Обработка текстовой задачи	\N	taskprocessing	\N	\N	\N
14	Недоступен	\N	unavailable	\N	\N	\N
15	Нерабочее время	\N	offline	\N	\N	\N
16	Уволен	\N	dismiss	\N	\N	\N
\.


--
-- Data for Name: user_groups; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.user_groups (user_id, group_id) FROM stdin;
70	1
71	1
79	1
80	1
84	1
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.user_roles (user_id, role_id) FROM stdin;
70	1
71	1
79	1
79	2
79	3
80	1
84	1
\.


--
-- Data for Name: user_skills; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.user_skills (user_id, role_id) FROM stdin;
69	1
70	1
71	1
71	2
79	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.users (id, email, hashed_password, password, name, last_name, patronymic, fio, login, is_operator, phone, is_active, photo_path, position_id, status_id, date_employment_at, date_dismissal_at, created_at, updated_at, status_at, department_id, image_id, personal_number, employment_status, uuid) FROM stdin;
0	admin@mail.py	15e2b0d3c33891ebb0f1ef609ec419420c20e320ce94c65fbc8c3312448eb225	123456789	admin	admin	admin	admin admin admin	admin	\N	\N	f	\N	\N	\N	\N	2023-03-15 10:21:56.898	2023-02-09 16:48:26.152263	2023-03-15 10:43:23.419038	2023-03-15 10:21:56.898	\N	\N	\N	t	41cc307f-abdf-4896-a30a-456caf875680
71	test_deparmnet@mail.ru	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	123	Тест	Тестович	Тестик	Тестович Тест Тестик	deparments	\N	89040856012	t	\N	\N	\N	2023-03-15 11:59:49.353	\N	2023-03-15 12:01:39.386079	2023-03-16 11:23:22.680376	2023-03-16 14:23:22.682885	1	\N	number-098	t	fecec5ba-633d-41c7-b9b2-7f8d55aea504
84	test_mail@mail.py	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	123	123	123	123	123 123 123	test_mail	t	string	t	\N	\N	\N	2023-04-10 13:03:51.262	\N	2023-04-10 13:11:06.139596	2023-04-10 13:11:06.347198	2023-04-10 16:11:06.365293	\N	\N	string	t	\N
79	items@mail.ru	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	123	Тест	Тестов	Тестович	Тестов Тест Тестович	teset_1	f	88002000600	t	\N	1	\N	2023-03-29 08:29:57.119	\N	2023-03-29 11:10:03.088624	2023-03-29 11:10:03.220073	2023-03-29 14:10:03.233565	6	\N	n-321	t	fee4f73b-9395-436a-8a58-fcaa3398b594
80	test_user@mail.ru	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	123	Test User	testing	Тестович	testing Test User Тестович	test_user	\N	string	t	\N	\N	\N	2023-04-03 11:06:19.816	\N	2023-04-03 11:34:28.586763	2023-04-03 11:38:10.096966	2023-04-03 14:34:49.023025	\N	\N	string	t	95fd4c2e-a18f-4556-999a-576f6bc4e81d
69	string	473287f8298dba7163a897908958f7c0eae733e25d2e027992ea2edc9bed2fa8	string	string	string	string	string string string	string	t	string	t	\N	\N	10	2023-04-10 13:16:08.277	2023-04-10 13:07:31.115532	2023-03-13 07:43:03.582887	2023-04-11 14:29:43.603718	2023-04-11 15:52:38	\N	\N	string	t	559f740b-b216-473b-8bd9-372796ceffb0
70	test_user1@mail.ru	a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3	123	user	last_name	patronymic	last_name user patronymic	login1	t	89040856012	t	\N	1	\N	2023-03-13 07:43:35.525	\N	2023-03-13 08:34:48.223036	2023-03-13 08:34:48.434062	2023-03-13 11:34:48.437097	6	\N	test-123	t	1d96b223-1e4b-4310-b4bd-a47925425931
\.


--
-- Data for Name: users_permission; Type: TABLE DATA; Schema: public; Owner: project
--

COPY public.users_permission (id, user_id, role_id, module_id, is_active, is_available, method_access) FROM stdin;
57	79	1	1	t	t	11101
109	69	1	2	t	t	00000
110	69	1	3	t	t	00000
111	69	1	1	t	t	10000
112	69	2	1	t	t	00000
113	69	2	2	t	t	00000
114	69	2	3	t	t	00000
115	69	3	1	t	t	11111
116	69	3	2	t	t	00000
117	69	3	3	t	t	00000
118	80	1	2	t	t	00000
119	80	1	3	t	t	00000
120	80	1	1	t	t	01000
55	79	1	2	t	t	00000
56	79	1	3	t	t	00000
58	79	2	1	t	t	00000
59	79	2	2	t	t	00000
60	79	2	3	t	t	00000
61	79	3	1	t	t	11111
62	79	3	2	t	t	00000
63	79	3	3	t	t	00000
127	84	1	2	t	t	00000
128	84	1	3	t	t	00000
129	84	1	1	t	t	01000
\.


--
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.departments_id_seq', 21, true);


--
-- Name: groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.groups_id_seq', 2, true);


--
-- Name: head_of_depatments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.head_of_depatments_id_seq', 21, true);


--
-- Name: images_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.images_id_seq', 6, true);


--
-- Name: inner_phones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.inner_phones_id_seq', 13, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.permissions_id_seq', 36, true);


--
-- Name: position_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.position_id_seq', 1, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- Name: skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.skills_id_seq', 3, true);


--
-- Name: status_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.status_history_id_seq', 137, true);


--
-- Name: status_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.status_users_id_seq', 20, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.users_id_seq', 84, true);


--
-- Name: users_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: project
--

SELECT pg_catalog.setval('public.users_permission_id_seq', 129, true);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: head_of_departments head_of_depatments_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.head_of_departments
    ADD CONSTRAINT head_of_depatments_pkey PRIMARY KEY (id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (id);


--
-- Name: inner_phones inner_phones_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.inner_phones
    ADD CONSTRAINT inner_phones_pkey PRIMARY KEY (id);


--
-- Name: inner_phones inner_phones_uuid_key; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.inner_phones
    ADD CONSTRAINT inner_phones_uuid_key UNIQUE (uuid);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: position position_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public."position"
    ADD CONSTRAINT position_pkey PRIMARY KEY (id);


--
-- Name: roles_permission roles_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.roles_permission
    ADD CONSTRAINT roles_permission_pkey PRIMARY KEY (id, role_id, module_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: skills skills_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);


--
-- Name: status_history status_history_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.status_history
    ADD CONSTRAINT status_history_pkey PRIMARY KEY (id);


--
-- Name: status_users status_users_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.status_users
    ADD CONSTRAINT status_users_pkey PRIMARY KEY (id);


--
-- Name: user_groups user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_pkey PRIMARY KEY (user_id, group_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: user_skills user_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT user_skills_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_login_key; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_login_key UNIQUE (login);


--
-- Name: users_permission users_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users_permission
    ADD CONSTRAINT users_permission_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_uuid_key; Type: CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_uuid_key UNIQUE (uuid);


--
-- Name: dep_graph fk_child_id; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.dep_graph
    ADD CONSTRAINT fk_child_id FOREIGN KEY (child_id) REFERENCES public.departments(id);


--
-- Name: dep_graph fk_parent_id; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.dep_graph
    ADD CONSTRAINT fk_parent_id FOREIGN KEY (parent_id) REFERENCES public.departments(id);


--
-- Name: head_of_departments head_of_depatments_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.head_of_departments
    ADD CONSTRAINT head_of_depatments_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id);


--
-- Name: head_of_departments head_of_depatments_deputy_head_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.head_of_departments
    ADD CONSTRAINT head_of_depatments_deputy_head_id_fkey FOREIGN KEY (deputy_head_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: head_of_departments head_of_depatments_head_of_depatment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.head_of_departments
    ADD CONSTRAINT head_of_depatments_head_of_depatment_id_fkey FOREIGN KEY (head_of_department_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: inner_phones inner_phones_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.inner_phones
    ADD CONSTRAINT inner_phones_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: roles_permission roles_permission_module_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.roles_permission
    ADD CONSTRAINT roles_permission_module_id_fkey FOREIGN KEY (module_id) REFERENCES public.permissions(id);


--
-- Name: roles_permission roles_permission_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.roles_permission
    ADD CONSTRAINT roles_permission_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: status_history status_history_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.status_history
    ADD CONSTRAINT status_history_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_users(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: status_history status_history_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.status_history
    ADD CONSTRAINT status_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_groups user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: user_groups user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: user_skills user_skills_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT user_skills_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.skills(id);


--
-- Name: user_skills user_skills_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.user_skills
    ADD CONSTRAINT user_skills_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: users users_department_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_department_id_fkey FOREIGN KEY (department_id) REFERENCES public.departments(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: users users_image_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_image_id_fkey FOREIGN KEY (image_id) REFERENCES public.images(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: users_permission users_permission_module_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users_permission
    ADD CONSTRAINT users_permission_module_id_fkey FOREIGN KEY (module_id) REFERENCES public.permissions(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: users_permission users_permission_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users_permission
    ADD CONSTRAINT users_permission_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: users_permission users_permission_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users_permission
    ADD CONSTRAINT users_permission_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: users users_position_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_position_id_fkey FOREIGN KEY (position_id) REFERENCES public."position"(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: users users_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: project
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_users(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

