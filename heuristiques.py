# Structure en classes peu utile dans notre cas d'utilisation
#
# class Heuristique:
#     def __init__(self, nom , emplacement):
#         self.nom = nom
#         self.emplacement = emplacement
#
# class BorneInferieur(Heuristique):
#     def __init__(self):
#         super().__init__("Borne Inférieur","BorneInf")
#
# class BorneSuperieur(Heuristique):
#     def __init__(self):
#         super().__init__("Borne Inférieur","BorneInf")
#
# class Gloutonne(Heuristique):
#     def __init__(self):
#         super().__init__("Gloutonne","Gloutonne")

def gloutonne(cache_server_capacity,videos, endpoints, cache_servers, requests ):
    print('start sorting servers')
    sorted_cache_servers = sorted(cache_servers, key=lambda c: -c.score(videos))
    # sorted_cache_servers = cache_servers
    print('finish sorting servers')
    # print(sorted_cache_servers, [c.score(videos) for c in sorted_cache_servers])
    for cache_server in sorted_cache_servers:
        print('{} {}'.format(cache_server.id, len(cache_servers)), sep=' ', end='', flush=True)
        video_sum = 0
        video_score = {}
        for endpoint in cache_server.endpoints:
            for request in endpoint.requests:
                video = videos[request.video_id]
                result = (
                    endpoint.latency_to_datacenter_norm - endpoint.get_cache_server_latency_norm(cache_server.id)
                ) * video.ratio_endpoint_norm(endpoint.id)
                if request.video_id in video_score:
                    video_score[request.video_id] += result
                else:
                    video_score[request.video_id] = result
        video_score_enumerated = video_score.items()
        sorted_video_score_enumerated = sorted(video_score_enumerated, key=lambda x: -x[1])

        cache_filled_status = 0
        # print(video_score)
        for (index, score) in sorted_video_score_enumerated:
            if score == 0:
                break
            video = videos[index]
            if (cache_filled_status + video.size > cache_server.size):
                continue
            cache_filled_status += video.size
            cache_server.append_video(video)
            for endpoint in cache_server.endpoints:
                endpoint.remove_requests(video.id)

    return cache_servers

