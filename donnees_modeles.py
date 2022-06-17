from dataclasses import dataclass, field


@dataclass
class DonneesLus:
    capacite_stockage : int
    videos_liste: list
    endpoints_liste: list
    cache_serveur_liste: list
    requetes_liste: list


@dataclass
class Videos:
    id : int
    size: int
    requests : list = field(default_factory=list)
    popularity_per_endpoint_cache : dict = field(default_factory=dict)
    popularity_per_endpoint_cache_norm : dict = field(default_factory=dict)
    size_norm : None = None

    def append_request(self, request):
        self.requests.append(request)

    def ratio_endpoint(self, endpoint_id):
        return self.popularity_per_endpoint(endpoint_id) / self.size

    def ratio_endpoint_norm(self, endpoint_id):
        return self.popularity_per_endpoint_norm(endpoint_id) / self.size

    def normalize_size(self, videos_size):
        self.size_norm = (self.size / videos_size)

    def popularity(self):
        return sum([request.number_of_requests for request in self.requests])

    def popularity_per_endpoint(self, endpoint_id):
        if endpoint_id in self.popularity_per_endpoint_cache:
            return self.popularity_per_endpoint_cache[endpoint_id]
        result = sum([request.number_of_requests for request in self.requests if request.endpoint_id == endpoint_id])
        self.popularity_per_endpoint_cache[endpoint_id] = result
        return result

    def popularity_per_endpoint_norm(self, endpoint_id):
        if endpoint_id in self.popularity_per_endpoint_cache_norm:
            return self.popularity_per_endpoint_cache_norm[endpoint_id]
        result = sum([request.number_of_requests_norm for request in self.requests if request.endpoint_id == endpoint_id])
        self.popularity_per_endpoint_cache_norm[endpoint_id] = result
        return result


@dataclass
class Endpoints:
    id : int
    latency_to_datacenter : int
    cache_servers_with_latency : int
    latency_to_datacenter_norm : None = None
    requests : list = field(default_factory=list)
    cache_servers_with_latency_norm : list = field(default_factory=list)
    get_cache_server_latency_norm_cache : dict = field(default_factory=dict)

    def normalize_latency(self, latency_sum):
        self.latency_to_datacenter_norm = self.latency_to_datacenter / latency_sum
        for cache_server in self.cache_servers_with_latency:
            self.cache_servers_with_latency_norm.append({
                'cache_id': cache_server['cache_id'],
                'latency_norm': cache_server['latency'] / latency_sum
            })

    def get_cache_server_latency (self, cache_server_id):
        return [cache_server['latency'] for cache_server in self.cache_servers_with_latency if cache_server_id == cache_server['cache_id']][0]

    def get_cache_server_latency_norm (self, cache_server_id):
        if cache_server_id in self.get_cache_server_latency_norm_cache:
            return self.get_cache_server_latency_norm_cache[cache_server_id]
        result = [cache_server['latency_norm'] for cache_server in self.cache_servers_with_latency_norm if cache_server_id == cache_server['cache_id']][0]
        self.get_cache_server_latency_norm_cache[cache_server_id] = result
        return result

    def remove_requests(self, video_id):
        self.requests = [request for request in self.requests if request.video_id != video_id]

    def append_request(self, request):
        self.requests.append(request)


@dataclass
class Cache_Serveur:
    id : int
    size : int
    endpoints : list = field(default_factory=list)
    videos : list = field(default_factory=list)


    def append_endpoint(self, endpoint):

        self.endpoints.append(endpoint)

    def append_video(self, video):
        self.videos.append(video)

    def score(self, videos):
        result = 0
        for endpoint in self.endpoints:
            # print('endpoint {} {}'.format(endpoint.id, len(self.endpoints)), flush=True)
            videos_ratio = 0
            for request in endpoint.requests:
                video = videos[request.video_id]
                videos_ratio += video.ratio_endpoint_norm(endpoint.id)
            result += (endpoint.latency_to_datacenter_norm - endpoint.get_cache_server_latency_norm(self.id)) * videos_ratio
        return result

@dataclass
class Requetes:
    video_id : int
    endpoint_id : int
    number_of_requests : int
    number_of_requests_norm : None = None


    def normalize_number_of_requests(self, request_sum):
        self.number_of_requests_norm = self.number_of_requests / request_sum
