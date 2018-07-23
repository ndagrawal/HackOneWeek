using System.Collections.Generic;
using System.Runtime.Serialization;

namespace WebApplication1.Controllers
{
    [DataContract]
    public class Response
    {
        [DataMember]
        public IList<AreaResult> areas { get; set; }

        [DataMember]
        public IList<UsersResult> users { get; set; }

        [DataMember]
        public IList<PullRequestResult> pullRequests { get; set; }

        [DataMember]
        public IList<WorkItemResult> workItems { get; set; }

    }

    [DataContract]
    public class WorkItemResult
    {
        [DataMember]
        public int id { get; set; }

        [DataMember]
        public string confidence { get; set; }
    }

    [DataContract]
    public class PullRequestResult
    {
        [DataMember]
        public int id { get; set; }

        [DataMember]
        public string confidence { get; set; }
    }

    [DataContract]
    public class UsersResult
    {
        [DataMember]
        public string tfid { get; set; }

        [DataMember]
        public string confidence { get; set; }
    }

    [DataContract]
    public class AreaResult
    {
        [DataMember]
        public int id { get; set; }

        [DataMember]
        public string confidence { get; set; }
    }
}