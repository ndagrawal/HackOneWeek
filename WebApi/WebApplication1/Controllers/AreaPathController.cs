using Newtonsoft.Json;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Runtime.Serialization;

using System.Web.Http;

namespace WebApplication1.Controllers
{
    public class AreaPathController : ApiController
    {
        // POST: api/AreaPath
        public AreaPathPredictions Post(Request value)
        {
            //var response = new HttpClient().PostAsJsonAsync("http://localhost:5000/areapath", value).Result;
            //var json = response.Content.ReadAsStringAsync().Result;
            //var result = JsonConvert.DeserializeObject<Response>(json);

            return GetDummyResponse();
        }


        public HttpResponseMessage Options()
        {
            return new HttpResponseMessage { StatusCode = HttpStatusCode.OK };
        }

        private AreaPathPredictions GetDummyResponse()
        {
            return new AreaPathPredictions
            {
                predictions = new List<AreaPathPrediction>
                {
                    new AreaPathPrediction{areapath="VSOnline/sample", probability=0.95f},
                    new AreaPathPrediction{areapath="VSOnline/sample", probability=0.95f},
                    new AreaPathPrediction{areapath="VSOnline/sample", probability=0.95f}
                }
            };
        }
    }

    [DataContract]
    public class AreaPathResponse
    {
        [DataMember]
        public string area { get; set; }
    }

    [DataContract]
    public class AreaPathPrediction
    {
        [DataMember]
        public string areapath;

        [DataMember]
        public float probability;
    }

    [DataContract]
    public class AreaPathPredictions
    {
        [DataMember]
        public IEnumerable<AreaPathPrediction> predictions;
    }
}
