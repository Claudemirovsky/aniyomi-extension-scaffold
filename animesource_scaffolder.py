import os
from textwrap import dedent

class AnimeSourceScaffolder:
    def __init__(self, is_parsed: bool, name: str, lang: str, baseUrl: str):
        self.className = "".join(filter(str.isalnum, name))  # Remove special chars
        # Prevent (kt)lint error: "Classnames should start in uppercase!"
        firstChar = self.className[0]
        if firstChar.islower():
            self.className = firstChar.upper() + self.className[1:]
        self.package = self.className.lower()
        self.is_parsed = is_parsed
        self.name = name
        self.lang = lang
        if "-" in lang:
            # en-US -> en, pt-BR -> pt
            self.short_lang = lang[: lang.find("-")]
        else:
            self.short_lang = lang

        self.baseUrl = baseUrl.strip("/")

        self.package_path = f"src/{self.short_lang}/{self.package}"
        self.package_id = f"{self.short_lang}.{self.package}"
        self.resources_path = f"{self.package_path}/res"
        self.sources_path = f"{self.package_path}/src/eu/kanade/tachiyomi/animeextension/{self.short_lang}/{self.package}"

    def create_dirs(self):
        try:
            os.makedirs(self.sources_path)
            os.makedirs(self.resources_path)
        except:
            pass

    def create_files(self):
        files = (
            (f"{self.package_path}/AndroidManifest.xml", self.android_manifest),
            (f"{self.package_path}/build.gradle", self.build_gradle),
            (f"{self.sources_path}/{self.className}.kt", self.default_class),
            (f"{self.sources_path}/{self.className}UrlActivity.kt", self.url_handler),
        )

        for file, content in files:
            print(f"Creating {file}")
            with open(file, "w+", encoding="utf-8") as f:
                f.write(content)

    @property
    def default_class(self):
        if self.is_parsed:
            return self.parsed_http_source
        else:
            return self.http_source

    @property
    def android_manifest(self) -> str:
        host = self.baseUrl.replace("https://", "", 1)
        return dedent(f"""
        <?xml version="1.0" encoding="utf-8"?>
        <manifest xmlns:android="http://schemas.android.com/apk/res/android">
            <application>
                <activity
                    android:name=".{self.package_id}.{self.className}UrlActivity"
                    android:excludeFromRecents="true"
                    android:exported="true"
                    android:theme="@android:style/Theme.NoDisplay">
                    <intent-filter>
                        <action android:name="android.intent.action.VIEW" />

                        <category android:name="android.intent.category.DEFAULT" />
                        <category android:name="android.intent.category.BROWSABLE" />

                        <data
                            android:host="{host}"
                            android:pathPattern="/anime/..*"
                            android:scheme="https" />
                    </intent-filter>
                </activity>
            </application>
        </manifest>
        """[1:])

    @property
    def build_gradle_plugins(self) -> str:
        return dedent(f"""
        plugins {{
            alias(libs.plugins.android.application)
            alias(libs.plugins.kotlin.android)
            {"alias(libs.plugins.kotlin.serialization)" if not self.is_parsed else ""}
        }}"""[1:]).replace("\n\n}", "\n}") + "\n\n"

    @property
    def build_gradle(self) -> str:
        return self.build_gradle_plugins + dedent(f"""
        ext {{
            extName = '{self.name}'
            pkgNameSuffix = '{self.package_id}'
            extClass = '.{self.className}'
            extVersionCode = 1
        }}

        apply from: "$rootDir/common.gradle"
        """[1:])

    @property
    def http_source_screens(self) -> str:
        return f"""
            // ============================== Popular ===============================
            override fun popularAnimeRequest(page: Int): Request {{
                throw UnsupportedOperationException()
            }}

            override fun popularAnimeParse(response: Response): AnimesPage {{
                throw UnsupportedOperationException()
            }}

            // =============================== Latest ===============================
            override fun latestUpdatesRequest(page: Int): Request {{
                throw UnsupportedOperationException()
            }}

            override fun latestUpdatesParse(response: Response): AnimesPage {{
                throw UnsupportedOperationException()
            }}

            // =============================== Search ===============================
{self.url_handler_search}

            override fun searchAnimeRequest(page: Int, query: String, filters: AnimeFilterList): Request {{
                throw UnsupportedOperationException()
            }}

            override fun searchAnimeParse(response: Response): AnimesPage {{
                throw UnsupportedOperationException()
            }}

            // =========================== Anime Details ============================
            override fun animeDetailsParse(response: Response): SAnime {{
                throw UnsupportedOperationException()
            }}

            // ============================== Episodes ==============================
            override fun episodeListParse(response: Response): List<SEpisode> {{
                throw UnsupportedOperationException()
            }}"""[1:]

    @property
    def http_source_catalogues(self) -> str:
        return """
            // ============================ Video Links =============================
            override fun videoListRequest(episode: SEpisode): Request {
                throw UnsupportedOperationException()
            }

            override fun videoListParse(response: Response): List<Video> {
                throw UnsupportedOperationException()
            }"""[1:]

    @property
    def http_source(self) -> str:
        return dedent(f"""
        package eu.kanade.tachiyomi.animeextension.{self.package_id}

        import eu.kanade.tachiyomi.animesource.model.AnimeFilterList
        import eu.kanade.tachiyomi.animesource.model.AnimesPage
        import eu.kanade.tachiyomi.animesource.model.SAnime
        import eu.kanade.tachiyomi.animesource.model.SEpisode
        import eu.kanade.tachiyomi.animesource.model.Video
        import eu.kanade.tachiyomi.animesource.online.AnimeHttpSource
        import eu.kanade.tachiyomi.network.GET
        import eu.kanade.tachiyomi.network.asObservableSuccess
        import kotlinx.serialization.json.Json
        import kotlinx.serialization.json.decodeFromStream
        import okhttp3.Request
        import okhttp3.Response
        import rx.Observable
        import uy.kohesive.injekt.injectLazy

        class {self.className} : AnimeHttpSource() {{

            override val name = "{self.name}"

            override val baseUrl = "{self.baseUrl}"

            override val lang = "{self.lang}"

            override val supportsLatest = false

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
        return f"""
            // ============================== Popular ===============================
            override fun popularAnimeRequest(page: Int): Request {{
                throw UnsupportedOperationException()
            }}

            override fun popularAnimeSelector(): String {{
                throw UnsupportedOperationException()
            }}

            override fun popularAnimeFromElement(element: Element): SAnime {{
                throw UnsupportedOperationException()
            }}

            override fun popularAnimeNextPageSelector(): String? {{
                throw UnsupportedOperationException()
            }}

            // =============================== Latest ===============================
            override fun latestUpdatesRequest(page: Int): Request {{
                throw UnsupportedOperationException()
            }}

            override fun latestUpdatesSelector(): String {{
                throw UnsupportedOperationException()
            }}

            override fun latestUpdatesFromElement(element: Element): SAnime {{
                throw UnsupportedOperationException()
            }}

            override fun latestUpdatesNextPageSelector(): String? {{
                throw UnsupportedOperationException()
            }}

            // =============================== Search ===============================
{self.url_handler_search}

            override fun searchAnimeRequest(page: Int, query: String, filters: AnimeFilterList): Request {{
                throw UnsupportedOperationException()
            }}

            override fun searchAnimeSelector(): String {{
                throw UnsupportedOperationException()
            }}

            override fun searchAnimeFromElement(element: Element): SAnime {{
                throw UnsupportedOperationException()
            }}

            override fun searchAnimeNextPageSelector(): String? {{
                throw UnsupportedOperationException()
            }}

            // =========================== Anime Details ============================
            override fun animeDetailsParse(document: Document): SAnime {{
                throw UnsupportedOperationException()
            }}
            
            // ============================== Episodes ==============================
            override fun episodeListSelector(): String {{
                throw UnsupportedOperationException()
            }}

            override fun episodeFromElement(element: Element): SEpisode {{
                throw UnsupportedOperationException()
            }}"""[1:]

    @property
    def parsed_http_source_catalogues(self) -> str:
        return """
            // ============================ Video Links =============================
            override fun videoListParse(response: Response): List<Video> {
                throw UnsupportedOperationException()
            }

            override fun videoListSelector(): String {
                throw UnsupportedOperationException()
            }

            override fun videoFromElement(element: Element): Video {
                throw UnsupportedOperationException()
            }

            override fun videoUrlParse(document: Document): String {
                throw UnsupportedOperationException()
            }"""[1:]

    @property
    def parsed_http_source(self) -> str:
        return dedent(f"""
        package eu.kanade.tachiyomi.animeextension.{self.package_id}

        import eu.kanade.tachiyomi.animesource.model.AnimeFilterList
        import eu.kanade.tachiyomi.animesource.model.AnimesPage
        import eu.kanade.tachiyomi.animesource.model.SAnime
        import eu.kanade.tachiyomi.animesource.model.SEpisode
        import eu.kanade.tachiyomi.animesource.model.Video
        import eu.kanade.tachiyomi.animesource.online.ParsedAnimeHttpSource
        import eu.kanade.tachiyomi.network.GET
        import eu.kanade.tachiyomi.network.asObservableSuccess
        import eu.kanade.tachiyomi.util.asJsoup
        import okhttp3.Request
        import okhttp3.Response
        import org.jsoup.nodes.Document
        import org.jsoup.nodes.Element
        import rx.Observable

        class {self.className} : ParsedAnimeHttpSource() {{

            override val name = "{self.name}"

            override val baseUrl = "{self.baseUrl}"

            override val lang = "{self.lang}"

            override val supportsLatest = false

{self.parsed_http_source_screens}

{self.parsed_http_source_catalogues}

            companion object {{
                const val PREFIX_SEARCH = "id:"
            }}
        }}
        """[1:])

    @property
    def url_handler(self) -> str:
        return dedent(f"""
        package eu.kanade.tachiyomi.animeextension.{self.package_id}

        import android.app.Activity
        import android.content.ActivityNotFoundException
        import android.content.Intent
        import android.os.Bundle
        import android.util.Log
        import kotlin.system.exitProcess

        /**
         * Springboard that accepts {self.baseUrl}/anime/<item> intents
         * and redirects them to the main Aniyomi process.
         */
        class {self.className}UrlActivity : Activity() {{

            private val tag = javaClass.simpleName

            override fun onCreate(savedInstanceState: Bundle?) {{
                super.onCreate(savedInstanceState)
                val pathSegments = intent?.data?.pathSegments
                if (pathSegments != null && pathSegments.size > 1) {{
                    val item = pathSegments[1]
                    val mainIntent = Intent().apply {{
                        action = "eu.kanade.tachiyomi.ANIMESEARCH"
                        putExtra("query", "${{{self.className}.PREFIX_SEARCH}}$item")
                        putExtra("filter", packageName)
                    }}

                    try {{
                        startActivity(mainIntent)
                    }} catch (e: ActivityNotFoundException) {{
                        Log.e(tag, e.toString())
                    }}
                }} else {{
                    Log.e(tag, "could not parse uri from intent $intent")
                }}

                finish()
                exitProcess(0)
            }}
        }}
        """[1:])

    @property
    def url_handler_search(self) -> str:
        return f"""
            override fun fetchSearchAnime(page: Int, query: String, filters: AnimeFilterList): Observable<AnimesPage> {{
                return if (query.startsWith(PREFIX_SEARCH)) {{ // URL intent handler
                    val id = query.removePrefix(PREFIX_SEARCH)
                    client.newCall(GET("$baseUrl/anime/$id"))
                        .asObservableSuccess()
                        .map(::searchAnimeByIdParse)
                }} else {{
                    super.fetchSearchAnime(page, query, filters)
                }}
            }}

            private fun searchAnimeByIdParse(response: Response): AnimesPage {{
                val details = animeDetailsParse(response{".use { it.asJsoup() }" if self.is_parsed else ""})
                return AnimesPage(listOf(details), false)
            }}"""[1:]
