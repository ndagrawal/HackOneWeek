using System.Collections.Generic;
using System.Net.Http;
using System.Web.Http;
using Newtonsoft.Json;
using System.Net;

namespace WebApplication1.Controllers
{
    public class SimilarWorkItemsController : ApiController
    {
        public Response Post(Request value)
        {
            try
            {
                var response = new HttpClient().PostAsJsonAsync("http://localhost:5000/similar", value).Result;

                var json = response.Content.ReadAsStringAsync().Result;

                var result = JsonConvert.DeserializeObject<Response>(json);
            }
            catch
            {
                // catch everything now
            }
            return GetDummyResponse();
        }

        public HttpResponseMessage Options()
        {
            return new HttpResponseMessage { StatusCode = HttpStatusCode.OK };
        }

        private Response GetDummyResponse()
        {
            return new Response
            {
                areas = new List<AreaResult>
                {
                    new AreaResult{confidence="High", id=4156},
                    new AreaResult{confidence="Medium", id=4153},
                    new AreaResult{confidence="Low", id=15660}
                },
                users = new List<UsersResult>
                {
                    new UsersResult{confidence="High", tfid="4FC78215-D451-4A6A-802C-A55504F3CBCE"},
                    new UsersResult{confidence="Medium", tfid="6CE1F4D4-ADFC-4090-A37C-542DA337AE65"},
                    new UsersResult{confidence="Low", tfid="5DC15C23-0B20-46A2-AF35-BBFE6DDCDEB5"}
                },
                workItems = new List<WorkItemResult>
                {
                    new WorkItemResult{confidence="High", id=1146918},
                    new WorkItemResult{confidence="Medium", id=1248434},
                    new WorkItemResult{confidence="Low", id=1237767},
                },
                pullRequests = new List<PullRequestResult>
                {
                    new PullRequestResult{confidence="High", id=336348},
                    new PullRequestResult{confidence="Medium", id=339808},
                    new PullRequestResult{confidence="Low", id=339760},
                },
            };
        }
    }

    public class Request
    {
        public string text { get; set; }
    }
}
