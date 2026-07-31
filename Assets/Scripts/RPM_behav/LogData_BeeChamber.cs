using System.Collections.Generic;
using UnityEngine;

public class LogData_BeeChamber : MonoBehaviour
{
    public uint amount_of_probes = 0;
    public List<Transform> probes = new List<Transform>();

    public List<Transform> GetAllProbes()
    {
        List<Transform> probes = new List<Transform>();
        foreach (Transform child in transform){
            if(child.name != "default")
            {
                probes.Add(child);
            }
        }
        return probes;
    }
    
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        amount_of_probes = (uint)this.transform.childCount-1;
        Debug.Log("Amount of Probes of BeeChamber: "+amount_of_probes);
        probes = GetAllProbes();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
