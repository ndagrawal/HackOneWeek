using Newtonsoft.Json;
using System.Net;
using System.Net.Http;
using System.Runtime.Serialization;
using System.Web.Http;

namespace WebApplication1.Controllers
{
    public class AreaPathController : ApiController
    {
        // POST: api/AreaPath
        public AreaPathResponse Post(Request value)
        {
            var response = new HttpClient().PostAsJsonAsync("http://localhost:5000/area", value).Result;

            var json = response.Content.ReadAsStringAsync().Result;

            return JsonConvert.DeserializeObject<AreaPathResponse>(json);

        }
        public HttpResponseMessage Options()
        {
            return new HttpResponseMessage { StatusCode = HttpStatusCode.OK };
        }
    }

    [DataContract]
    public class AreaPathResponse
    {
        [DataMember]
        public string area { get; set; }
    }
}
