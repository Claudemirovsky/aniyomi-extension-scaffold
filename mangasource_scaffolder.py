from textwrap import dedent
from animesource_scaffolder import AnimeSourceScaffolder

class MangaSourceScaffolder(AnimeSourceScaffolder):
    def __init__(self, is_parsed: bool, name: str, lang: str, baseUrl: str):
        super().__init__(is_parsed, name, lang, baseUrl)
        self.sources_path = f"{self.package_path}/src/eu/kanade/tachiyomi/extension/{self.short_lang}/{self.package}"

    replace_map = (
        ("AnimeFilterList", "FilterList"),
        ("Anime", "Manga"),
        ("Episode", "Chapter"),
        ("episode", "chapter"),
        ("anime", "manga"),
    )

    @property
    def android_manifest(self) -> str:
        return super().android_manifest.replace("/anime/", "/manga/")

    def convert_to_manga(self, input: str) -> str:
        output = input
        for (previous, new) in self.replace_map:
            output = output.replace(previous, new)
        return output

    @property
    def http_source_screens(self) -> str:
        return self.convert_to_manga(super().http_source_screens)

    @property
    def http_source_catalogues(self) -> str:
        return """
            // =============================== Pages ================================
            override fun pageListParse(response: Response): List<Page> {
                throw UnsupportedOperationException()
            }

            override fun imageUrlParse(response: Response): String {
                throw UnsupportedOperationException()
            }"""[1:]

    @property
    def http_source(self) -> str:
        return dedent(f"""
        package eu.kanade.tachiyomi.extension.{self.package_id}

        import eu.kanade.tachiyomi.network.GET
        import eu.kanade.tachiyomi.network.asObservableSuccess
        import eu.kanade.tachiyomi.network.interceptor.rateLimitHost
        import eu.kanade.tachiyomi.source.model.FilterList
        import eu.kanade.tachiyomi.source.model.MangasPage
        import eu.kanade.tachiyomi.source.model.Page
        import eu.kanade.tachiyomi.source.model.SChapter
        import eu.kanade.tachiyomi.source.model.SManga
        import eu.kanade.tachiyomi.source.online.HttpSource
        import kotlinx.serialization.json.Json
        import kotlinx.serialization.json.decodeFromStream
        import okhttp3.HttpUrl.Companion.toHttpUrl
        import okhttp3.Request
        import okhttp3.Response
        import rx.Observable
        import uy.kohesive.injekt.injectLazy

        class {self.className} : HttpSource() {{

            override val name = "{self.name}"

            override val baseUrl = "{self.baseUrl}"

            override val lang = "{self.lang}"

            override val supportsLatest = false

            override val client = network.client.newBuilder()
                .rateLimitHost(baseUrl.toHttpUrl(), 2)
                .build()

            private val json: Json by injectLazy()

{self.http_source_screens}

{self.http_source_catalogues}

            // ============================= Utilities ==============================
            private inline fun <reified T> Response.parseAs(): T = use {{
                json.decodeFromStream(it.body.byteStream())
            }}

            companion object {{
                const val PREFIX_SEARCH = "id:"
            }}
        }}
        """[1:])

    @property
    def parsed_http_source_screens(self) -> str:
        return self.convert_to_manga(super().parsed_http_source_screens)

    @property
    def parsed_http_source_catalogues(self) -> str:
        return """
            // =============================== Pages ================================
            override fun pageListParse(document: Document): List<Page> {
                throw UnsupportedOperationException()
            }

            override fun imageUrlParse(document: Document): String {
                throw UnsupportedOperationException()
            }"""[1:]

    @property
    def parsed_http_source(self) -> str:
        return dedent(f"""
        package eu.kanade.tachiyomi.extension.{self.package_id}

        import eu.kanade.tachiyomi.network.GET
        import eu.kanade.tachiyomi.network.asObservableSuccess
        import eu.kanade.tachiyomi.network.interceptor.rateLimitHost
        import eu.kanade.tachiyomi.source.model.FilterList
        import eu.kanade.tachiyomi.source.model.MangasPage
        import eu.kanade.tachiyomi.source.model.Page
        import eu.kanade.tachiyomi.source.model.SChapter
        import eu.kanade.tachiyomi.source.model.SManga
        import eu.kanade.tachiyomi.source.online.ParsedHttpSource
        import eu.kanade.tachiyomi.util.asJsoup
        import okhttp3.HttpUrl.Companion.toHttpUrl
        import okhttp3.Request
        import okhttp3.Response
        import org.jsoup.nodes.Document
        import org.jsoup.nodes.Element
        import rx.Observable

        class {self.className} : ParsedHttpSource() {{

            override val name = "{self.name}"

            override val baseUrl = "{self.baseUrl}"

            override val lang = "{self.lang}"

            override val supportsLatest = false

            override val client = network.client.newBuilder()
                .rateLimitHost(baseUrl.toHttpUrl(), 2)
                .build()

{self.parsed_http_source_screens}

{self.parsed_http_source_catalogues}

            companion object {{
                const val PREFIX_SEARCH = "id:"
            }}
        }}
        """[1:])

    @property
    def url_handler(self) -> str:
        return super().url_handler\
            .replace(".tachiyomi.anime", ".tachiyomi.")\
            .replace("/anime/", "/manga/")\
            .replace("ANIMESEARCH", "SEARCH")\
            .replace("Aniyomi", "Tachiyomi")

    @property
    def url_handler_search(self) -> str:
        return f"""
            override fun fetchSearchManga(page: Int, query: String, filters: FilterList): Observable<MangasPage> {{
                return if (query.startsWith(PREFIX_SEARCH)) {{ // URL intent handler
                    val id = query.removePrefix(PREFIX_SEARCH)
                    client.newCall(GET("$baseUrl/manga/$id"))
                        .asObservableSuccess()
                        .map(::searchMangaByIdParse)
                }} else {{
                    super.fetchSearchManga(page, query, filters)
                }}
            }}

            private fun searchMangaByIdParse(response: Response): MangasPage {{
                val details = mangaDetailsParse(response{".asJsoup()" if self.is_parsed else ""})
                    .apply {{ setUrlWithoutDomain(response.request.url.toString()) }}
                return MangasPage(listOf(details), false)
            }}"""[1:]
