--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8
-- Dumped by pg_dump version 16.8

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

--
-- Name: anime_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.anime_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.anime_id_seq OWNER TO aniblogtracker;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: anime; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.anime (
    anime_id bigint DEFAULT nextval('public.anime_id_seq'::regclass) NOT NULL,
    title character varying,
    synonyms character varying,
    mal_id bigint,
    anilist_id bigint,
    season character varying,
    year bigint
);


ALTER TABLE public.anime OWNER TO aniblogtracker;

--
-- Name: author_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.author_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.author_id_seq OWNER TO aniblogtracker;

--
-- Name: author; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.author (
    author_id bigint DEFAULT nextval('public.author_id_seq'::regclass) NOT NULL,
    site_id bigint,
    name character varying,
    bluesky character varying,
    mastodon character varying,
    lastupdated timestamp without time zone
);


ALTER TABLE public.author OWNER TO aniblogtracker;

--
-- Name: post_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.post_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.post_id_seq OWNER TO aniblogtracker;

--
-- Name: relatedanime_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.relatedanime_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.relatedanime_id_seq OWNER TO aniblogtracker;

--
-- Name: post_relatedanime; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.post_relatedanime (
    anime_id bigint,
    relatedanime_id bigint DEFAULT nextval('public.relatedanime_id_seq'::regclass) NOT NULL,
    post_id bigint
);


ALTER TABLE public.post_relatedanime OWNER TO aniblogtracker;

--
-- Name: posts; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.posts (
    post_id bigint DEFAULT nextval('public.post_id_seq'::regclass) NOT NULL,
    author_id bigint,
    site_id bigint,
    title character varying,
    content character varying,
    post_url character varying,
    thumbnail_filename character varying,
    published_date timestamp without time zone
);


ALTER TABLE public.posts OWNER TO aniblogtracker;

--
-- Name: site_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.site_id_seq OWNER TO aniblogtracker;

--
-- Name: site; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.site (
    site_id bigint DEFAULT nextval('public.site_id_seq'::regclass) NOT NULL,
    name character varying,
    description character varying,
    feed_url character varying,
    url character varying,
    sitetype_id bigint,
    favicon_lastupdated timestamp without time zone
);


ALTER TABLE public.site OWNER TO aniblogtracker;

--
-- Name: site_owners; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.site_owners (
    siteowner_id bigint NOT NULL,
    user_id bigint,
    site_id bigint
);


ALTER TABLE public.site_owners OWNER TO aniblogtracker;

--
-- Name: siteowner_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.siteowner_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.siteowner_id_seq OWNER TO aniblogtracker;

--
-- Name: siteowner_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: aniblogtracker
--

ALTER SEQUENCE public.siteowner_id_seq OWNED BY public.site_owners.siteowner_id;


--
-- Name: sitetype_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.sitetype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sitetype_id_seq OWNER TO aniblogtracker;

--
-- Name: sitetype; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.sitetype (
    sitetype_id bigint DEFAULT nextval('public.sitetype_id_seq'::regclass) NOT NULL,
    name character varying
);


ALTER TABLE public.sitetype OWNER TO aniblogtracker;

--
-- Name: subscription_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.subscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscription_id_seq OWNER TO aniblogtracker;

--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public.subscriptions (
    site_id bigint,
    user_id bigint,
    subscription_id bigint DEFAULT nextval('public.subscription_id_seq'::regclass) NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO aniblogtracker;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: aniblogtracker
--

CREATE SEQUENCE public.user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO aniblogtracker;

--
-- Name: user; Type: TABLE; Schema: public; Owner: aniblogtracker
--

CREATE TABLE public."user" (
    user_id bigint DEFAULT nextval('public.user_id_seq'::regclass) NOT NULL,
    is_admin boolean
);


ALTER TABLE public."user" OWNER TO aniblogtracker;

--
-- Name: site_owners siteowner_id; Type: DEFAULT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.site_owners ALTER COLUMN siteowner_id SET DEFAULT nextval('public.siteowner_id_seq'::regclass);


--
-- Name: anime anime_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.anime
    ADD CONSTRAINT anime_pk PRIMARY KEY (anime_id);


--
-- Name: author author_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.author
    ADD CONSTRAINT author_pk PRIMARY KEY (author_id);


--
-- Name: post_relatedanime post_relatedanime_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.post_relatedanime
    ADD CONSTRAINT post_relatedanime_pk PRIMARY KEY (relatedanime_id);


--
-- Name: posts posts_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pk PRIMARY KEY (post_id);


--
-- Name: site site_id; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.site
    ADD CONSTRAINT site_id PRIMARY KEY (site_id);


--
-- Name: site_owners site_owners_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.site_owners
    ADD CONSTRAINT site_owners_pk PRIMARY KEY (siteowner_id);


--
-- Name: sitetype sitetype_id_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.sitetype
    ADD CONSTRAINT sitetype_id_pk PRIMARY KEY (sitetype_id);


--
-- Name: subscriptions subscriptions_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pk PRIMARY KEY (subscription_id);


--
-- Name: user user_pk; Type: CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pk PRIMARY KEY (user_id);


--
-- Name: author author_site_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.author
    ADD CONSTRAINT author_site_fk FOREIGN KEY (site_id) REFERENCES public.site(site_id);


--
-- Name: post_relatedanime post_relatedanime_anime_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.post_relatedanime
    ADD CONSTRAINT post_relatedanime_anime_fk FOREIGN KEY (anime_id) REFERENCES public.anime(anime_id);


--
-- Name: post_relatedanime post_relatedanime_posts_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.post_relatedanime
    ADD CONSTRAINT post_relatedanime_posts_fk FOREIGN KEY (post_id) REFERENCES public.posts(post_id);


--
-- Name: posts posts_author_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_author_fk FOREIGN KEY (author_id) REFERENCES public.author(author_id);


--
-- Name: posts posts_site_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_site_fk FOREIGN KEY (site_id) REFERENCES public.site(site_id);


--
-- Name: site_owners site_owners_site_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.site_owners
    ADD CONSTRAINT site_owners_site_fk FOREIGN KEY (site_id) REFERENCES public.site(site_id);


--
-- Name: site_owners site_owners_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.site_owners
    ADD CONSTRAINT site_owners_user_fk FOREIGN KEY (user_id) REFERENCES public."user"(user_id);


--
-- Name: site site_sitetype_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.site
    ADD CONSTRAINT site_sitetype_fk FOREIGN KEY (sitetype_id) REFERENCES public.sitetype(sitetype_id);


--
-- Name: subscriptions subscriptions_site_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_site_fk FOREIGN KEY (site_id) REFERENCES public.site(site_id);


--
-- Name: subscriptions subscriptions_user_fk; Type: FK CONSTRAINT; Schema: public; Owner: aniblogtracker
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_fk FOREIGN KEY (user_id) REFERENCES public."user"(user_id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO aniblogtracker;


--
-- PostgreSQL database dump complete
--