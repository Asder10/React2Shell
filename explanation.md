# **The React2Shell Crisis: A Comprehensive Technical Analysis of CVE-2025-55182 and the Insecure Deserialization of the React Flight Protocol**

The disclosure of CVE-2025-55182, colloquially termed "React2Shell," marks a significant shift in the security landscape of modern JavaScript ecosystems. This vulnerability, characterized as a critical unauthenticated remote code execution (RCE) flaw, carries a maximum CVSS score of 10.0, indicating a worst-case scenario for organizations utilizing the React 19 ecosystem.1 At its core, the vulnerability resides within the implementation of the React Flight Protocol, a transport mechanism designed to facilitate communication between React Server Components (RSC) and the client.4 The impact of this flaw is intensified by its existence in default configurations, meaning that standard deployments of frameworks such as Next.js are inherently vulnerable without any specific developer error.1

## **Architectural Background and the Evolution of React Server Components**

To understand the mechanics of CVE-2025-55182, it is necessary to examine the architectural evolution that led to the introduction of React Server Components. Traditionally, web development relied on either Client-Side Rendering (CSR), where the browser executes JavaScript to build the user interface, or Server-Side Rendering (SSR), where the server generates a static HTML string sent to the client.6 RSC represents a paradigm shift by allowing individual components to execute on the server and stream their serialized output to the client for hydration.6

This architecture relies on the React Flight Protocol to bridge the gap between server execution and client rendering.4 Flight is a serialization format that goes beyond standard JSON by supporting the transmission of complex structures, including promises, element trees, and references between data chunks.6 When a client interacts with a server-side function, the browser packages the request—often as multipart form data—into numbered "chunks".6 The server then reassembles these chunks using internal resolution logic to reconstruct the intended function calls or data objects.5

### **The Role of the React Flight Protocol**

The Flight Protocol utilizes a system of specific markers or prefixes to denote various data types during the deserialization process.6 These markers allow the server to interpret strings as more than mere text, converting them into live references or specialized objects.5

| Prefix | Protocol Definition | Security Significance |
| :---- | :---- | :---- |
| $ | Identifies a reference to another chunk in the payload | Primary vector for prototype chain traversal via colon notation 9 |
| $@ | Denotes a reference to a "raw" internal Chunk object | Pivotal for creating self-referencing loops and gaining access to internal React states 5 |
| $B | Represents a Blob or binary data reference | Serves as the final execution gadget by invoking the \_formData.get method 6 |
| $F | Indicates a reference to a Server Function | Used for normal RPC-style communication between client and server 6 |
| $L | Points to a Lazy Component for deferred loading | Manages code splitting and progressive rendering 6 |

In a typical scenario, a request might be divided into multiple parts where chunk 0 points to chunk 1, and chunk 1 provides the arguments for a function call.6 The server-side logic responsible for this reassembly is primarily contained within the react-server package, specifically in modules like ReactFlightReplyServer.js.6

## **The Logic of the Vulnerability: Insecure Prototype Resolution**

The root cause of CVE-2025-55182 is an unsafe deserialization logic flaw within the React Flight Protocol's reference resolution mechanism.4 Prior to the critical patch released in December 2025, the protocol’s internal functions, such as reviveModel and getOutlinedModel, failed to validate whether the properties being requested in a reference were "own" properties of the object or inherited from the JavaScript prototype chain.6

### **Prototype Traversal via Colon Delimiters**

The protocol supports a colon-delimited syntax for navigating nested object properties within a reference.10 For example, a reference like $1:user:id would instruct the server to resolve chunk 1, access the user property, and then retrieve the id property from that user object.18 The vulnerable implementation processed these strings by splitting them at the colon and iteratively accessing the resulting keys.10

The absence of checks such as hasOwnProperty allowed an attacker to supply keys that exist on the prototype of all JavaScript objects.4 By crafting a reference such as $1:\_\_proto\_\_:constructor:constructor, an attacker could traverse from a standard object in a chunk to the global Function constructor.5 This is a classic "prototype pollution" or "prototype traversal" primitive that enables the acquisition of powerful internal JavaScript constructors that are normally inaccessible to user-controlled inputs.4

### **Duck-Typing and the Awaitable Exploit Vector**

The vulnerability's exploitability is deeply rooted in the way JavaScript handles asynchronous operations and the "thenable" interface.6 In JavaScript, the await keyword automatically resolves any object that possesses a .then() method.6 This behavior, known as "thenable" resolution, is used by the server-side action handler in frameworks like Next.js.9

In a vulnerable application, the function decodeReplyFromBusboy is responsible for parsing the incoming multipart stream.9 This function returns an object representing the root of the deserialized payload.9 The framework then immediately awaits this returned value:  
boundActionArguments \= await decodeReplyFromBusboy(...).9  
If an attacker can manipulate the deserialization process such that the returned object has a .then property pointing to a malicious function, the JavaScript runtime will execute that function as part of the normal await resolution process.9 This creates a direct path from an insecurely deserialized object to arbitrary code execution.9

## **Anatomy of the Exploitation Chain: The "React2Shell" Method**

The most sophisticated exploitation method for CVE-2025-55182, credited to the researcher maple3142, involves a multi-stage chain that hijacks internal React objects and redirects the execution flow to the Function constructor.6 This chain is designed to bypass security checks by forging "fake" internal chunks that the server trusts as legitimate.6

### **Stage 1: The Self-Reference and Raw Chunk Access**

The exploit begins by utilizing the $@ prefix to gain access to React's internal Chunk objects.6 Unlike the standard $ prefix, which returns the resolved value of a chunk, $@ returns the raw internal object that React uses to track the chunk's state (e.g., its status, value, and error information).6

By defining a chunk (e.g., chunk 1\) that references chunk 0 with $@0, and having chunk 0 reference chunk 1, the attacker creates a circular dependency.6 This loop allows the attacker to gain a reference to the internal Chunk object of chunk 0\.13

### **Stage 2: Hijacking the Then Handler and Forging Status**

The attacker then uses the prototype traversal primitive to set the .then property of chunk 0 to Chunk.prototype.then.6 Crucially, the attacker also sets the status field of chunk 0 to resolved\_model.6 This status code signals to the React parser that the chunk has been successfully received and is ready to be initialized into a component tree.13

When the framework awaits the result of the deserialization, it calls the overridden .then() on chunk 0\.13 Because the status is resolved\_model, the Chunk.prototype.then method automatically invokes the internal initializeModelChunk function, passing the attacker's fake chunk as the target.13

### **Stage 3: The Model Initialization Gadget**

During the initializeModelChunk phase, the server attempts to parse the .value property of the chunk as JSON and "revive" it into a model.6 This revival process allows for a second pass of reference resolution.6 The attacker crafts the .value field to include a reference to a Blob using the $B marker.6

The protocol's Blob handler attempts to retrieve binary data by calling a method on a controlled object:  
response.\_formData.get(response.\_prefix \+ obj).6  
In this context, the attacker fully controls the \_response property of the fake chunk.16 They can inject a malicious \_formData object where the get method is replaced with the global Function constructor, obtained via the $1:constructor:constructor path.5

### **Stage 4: Achieving Remote Code Execution**

The final stage of the exploit occurs when the Blob handler executes the call to the forged get method.12 The logic effectively becomes:  
Function(attacker\_code)()  
The attacker\_code is supplied via the \_prefix property.12 To prevent syntax errors that might arise from the protocol adding extra characters, the attacker appends a comment marker // to the end of their code.12 This allows for the execution of arbitrary shell commands or malicious scripts with the full privileges of the Node.js process.6

## **Ecosystem Impact and Vulnerability Range**

The "React2Shell" vulnerability has a profound impact across the modern web development landscape due to the deep integration of the React 19 architecture into numerous frameworks.1 Although initially tracked via separate identifiers—CVE-2025-55182 for React and CVE-2025-66478 for Next.js—the latter was eventually rejected as a duplicate, confirming that the root cause lies in the core React Server Components implementation.1

### **Affected Frameworks and Packages**

The vulnerability impacts any framework or library that bundles the react-server DOM packages or implements the Flight Protocol.23

| Product Category | Affected Versions | Mitigation Version |
| :---- | :---- | :---- |
| **React Core Packages** | 19.0.0, 19.1.0, 19.1.1, 19.2.0 4 | 19.0.1, 19.1.2, 19.2.1 3 |
| **Next.js (App Router)** | 15.x, 16.x, and Canary builds since 14.3.0-canary.77 4 | 15.0.5, 15.1.9, 16.0.7 (or latest patch) 3 |
| **Vite / Parcel Plugins** | Versions bundling affected react-server-dom-\* packages 19 | Framework/Plugin update 24 |
| **Other Frameworks** | Waku, RedwoodSDK, React Router (RSC mode), Expo 19 | Update React to 19.2.1+ 5 |

A critical detail for developers is that applications are vulnerable even if they do not explicitly define any Server Functions or Actions.1 The vulnerable Flight Protocol handler is active by default to support the App Router’s server-side rendering and hydration features.1 Consequently, an application with a single "Hello World" page built with the App Router in Next.js is potentially exploitable.28

## **Threat Intelligence: Observed Activity and Post-Exploitation Tactics**

Exploitation of CVE-2025-55182 in the wild began within hours of the public disclosure on December 3, 2025\.1 Threat intelligence gathered by Microsoft, Amazon, and Wiz has highlighted a rapid transition from proof-of-concept testing to weaponized attacks.1

### **Threat Actor Attribution**

China-nexus threat actors, including Earth Lamia and Jackpot Panda, were among the first to operationalize the vulnerability.5 These groups utilized automated scanning tools to identify vulnerable endpoints across the public internet.1

* **Earth Lamia**: This group has targeted financial services, logistics, and government organizations in Latin America, the Middle East, and Southeast Asia.5 They were observed established reverse shells and conducting reconnaissance shortly after the initial compromise.1  
* **Jackpot Panda**: Focused primarily on East and Southeast Asian sectors, this actor's activity aligns with domestic security and corruption intelligence priorities.5 They have been observed using the RCE to exfiltrate cloud credentials and system configurations.5

### **Common Post-Exploitation Payloads**

Attackers have leveraged the "React2Shell" flaw for a wide variety of malicious purposes, with a strong emphasis on credential harvesting and system persistence.1

* **Credential Theft**: Attackers target environment variables and cloud metadata services (IMDS) to steal identity tokens and API keys.1 Secret discovery tools like TruffleHog have been deployed to search the file system for OpenAI keys, database passwords, and SSH keys.1  
* **Cryptocurrency Mining**: Multiple campaigns have been observed dropping XMRig and other miners.1 These campaigns often use UPX-packed binaries and establish persistence via crontabs or systemd services.1  
* **Malware Frameworks**: In some instances, attackers have attempted to install the Sliver malware framework or deploy custom Linux droppers for long-term infection.7  
* **Evasion and Persistence**: To avoid detection, actors have utilized Cloudflare Tunnel endpoints and bind mounts to hide malicious processes and artifacts from monitoring tools.1

## **Detection Engineering: Identifying Malicious RSC Requests**

Detecting React2Shell exploitation requires a focus on the unique structure of the Flight Protocol and the headers used by frameworks like Next.js.5 Traditional signature-based detection can be challenged by the protocol’s flexibility and the possibility of obfuscation.5

### **Network-Based Indicators (WAF and Logs)**

The primary detection vectors involve monitoring HTTP POST requests to application endpoints for specific headers and payload patterns.5

* **Headers**: The presence of next-action or rsc-action-id is a key indicator, as these are required to trigger the server-side action handler.27 While these headers are legitimate, their appearance in requests with anomalous bodies should be flagged.30  
* **Payload Patterns**: The string $@ (used for raw chunk references) and "status":"resolved\_model" (used to forge the chunk state) are high-fidelity indicators of an exploitation attempt.5  
* **WAF Bypasses**: Attackers have already developed techniques to evade WAFs that only inspect the beginning of a request body.9 By prepending 128KB or more of junk data to the multipart form, the malicious Flight payload is pushed beyond the WAF's inspection window.9 More advanced bypasses specifically targeting Vercel's WAF have also been identified, utilizing additional form fields to confuse the filtering logic.18

### **Side-Channel Detection (Safe Scanning)**

For organizations seeking to identify vulnerable hosts without executing actual RCE payloads, a "safe check" method exists based on triggered exceptions.18 By sending a crafted multipart request where chunk 0 attempts to access an undefined property (e.g., \["$1:a:a"\] pointing to an empty object {}), a vulnerable server will crash during the reference resolution phase.18 This crash results in a 500 Internal Server Error with a characteristic response body: 1:E{"digest":"2971658870"}.18 This deterministic behavior allows for reliable identification of vulnerable versions without risk to the host's integrity.18

## **Remediation Strategies and Best Practices**

The critical nature of CVE-2025-55182 necessitates an immediate and comprehensive response from affected organizations.1 Patching is the only definitive way to close the vulnerability, but additional steps are required to ensure the security of previously exposed systems.5

### **The Patching Process**

Organizations must prioritize upgrading all affected React and framework packages to the recommended patched versions.3 Because subsequent vulnerabilities, including denial-of-service (CVE-2025-55184) and information leakage (CVE-2025-55183), were discovered shortly after the initial React2Shell disclosure, it is essential to update to the "definitive" patches.8

| Component | Minimum Definitive Safe Version | Action |
| :---- | :---- | :---- |
| **react** / **react-dom** | v19.0.3, v19.1.4, or v19.2.3 | Direct upgrade of peer dependencies 8 |
| **Next.js** | 15.5.7, 16.0.7, or latest in minor line | Framework-level update 3 |
| **Other Frameworks** | Latest released version | Check package-lock.json for nested React versions 8 |

Frameworks like Next.js have provided automated tools, such as npx fix-react2shell-next, to simplify the identification and remediation of vulnerable packages.5

### **Strategic Post-Patch Activities**

Following the update, organizations should assume that any internet-facing vulnerable server may have been compromised and take the following steps 22:

1. **Secret Rotation**: Immediately rotate all critical application secrets, including API keys, database credentials, and cloud access tokens.5  
2. **Incident Response Review**: Conduct a forensic audit of application logs for suspicious reconnaissance commands or unauthorized file access attempts (e.g., reading /etc/passwd).1  
3. **Network Segmentation**: Isolate application servers from sensitive internal databases and implement strict egress filtering to block connections to known command-and-control (C2) infrastructure.5  
4. **Runtime Monitoring**: Deploy Runtime Application Self-Protection (RASP) solutions that can detect and block anomalous code execution patterns within the Node.js runtime.3

## **Conclusion: Lessons from the React2Shell Incident**

The discovery and mass exploitation of CVE-2025-55182 serve as a landmark event in the history of JavaScript framework security.28 This vulnerability highlights the risks inherent in the complex, "magic" transport protocols that power modern web features like React Server Components.5 By blurring the line between client-side data and server-side execution logic, these protocols create high-privilege attack surfaces that require rigorous validation and security auditing.5

The rapid weaponization of this flaw by state-nexus threat actors demonstrates that the time between a critical vulnerability disclosure and its operational use is shrinking.11 For organizations, the React2Shell crisis underscores the importance of maintaining an accurate inventory of dependencies and a mature vulnerability management program that can respond to "upstream" flaws in hours rather than days. As the web development ecosystem continues to move more logic to the server, the security of the transport layer must remain a primary focus for both framework maintainers and the organizations that rely on them.

#### **Works cited**

1. Defending against the CVE-2025-55182 (React2Shell) vulnerability in React Server Components | Microsoft Security Blog, accessed December 22, 2025, [https://www.microsoft.com/en-us/security/blog/2025/12/15/defending-against-the-cve-2025-55182-react2shell-vulnerability-in-react-server-components/](https://www.microsoft.com/en-us/security/blog/2025/12/15/defending-against-the-cve-2025-55182-react2shell-vulnerability-in-react-server-components/)  
2. React2Shell, Critical unauthenticated RCE affecting React Server Components (CVE-2025-55182) \- Rapid7, accessed December 22, 2025, [https://www.rapid7.com/blog/post/etr-react2shell-cve-2025-55182-critical-unauthenticated-rce-affecting-react-server-components/](https://www.rapid7.com/blog/post/etr-react2shell-cve-2025-55182-critical-unauthenticated-rce-affecting-react-server-components/)  
3. React & Next.js CVE-2025-55182 / 66478 RCE \- Oligo Security, accessed December 22, 2025, [https://www.oligo.security/blog/critical-react-next-js-rce-vulnerability-cve-2025-55182-cve-2025-66478-what-you-need-to-know](https://www.oligo.security/blog/critical-react-next-js-rce-vulnerability-cve-2025-55182-cve-2025-66478-what-you-need-to-know)  
4. React2Shell RCE Vulnerability: CVE-2025-55182 and CVE-2025-66478 Explained, accessed December 22, 2025, [https://www.picussecurity.com/resource/blog/react-flight-protocol-rce-vulnerability-cve-2025-55182-and-cve-2025-66478-explained](https://www.picussecurity.com/resource/blog/react-flight-protocol-rce-vulnerability-cve-2025-55182-and-cve-2025-66478-explained)  
5. React2Shell (CVE-2025-55182) Critical Unauthenticated RCE \- SonicWall, accessed December 22, 2025, [https://www.sonicwall.com/blog/react2shell-cve-2025-55182-critical-unauthenticated-rce](https://www.sonicwall.com/blog/react2shell-cve-2025-55182-critical-unauthenticated-rce)  
6. CVE-2025-55182: React2Shell Analysis, Proof-of-Concept Chaos ..., accessed December 22, 2025, [https://www.trendmicro.com/en\_us/research/25/l/CVE-2025-55182-analysis-poc-itw.html](https://www.trendmicro.com/en_us/research/25/l/CVE-2025-55182-analysis-poc-itw.html)  
7. React2Shell (CVE-2025-55182): Critical React Vulnerability | Wiz Blog, accessed December 22, 2025, [https://www.wiz.io/blog/critical-vulnerability-in-react-cve-2025-55182](https://www.wiz.io/blog/critical-vulnerability-in-react-cve-2025-55182)  
8. Understanding and Mitigating CVE-2025-55182 (React2Shell) | UpGuard, accessed December 22, 2025, [https://www.upguard.com/blog/understanding-and-mitigating-cve-2025-55182-react2shell](https://www.upguard.com/blog/understanding-and-mitigating-cve-2025-55182-react2shell)  
9. React2Shell(CVE-2025–55182):Technical Deep Dive | MeetCyber \- Medium, accessed December 22, 2025, [https://medium.com/meetcyber/react2shell-cve-2025-55182-a-technical-deep-dive-da81ab27e99f](https://medium.com/meetcyber/react2shell-cve-2025-55182-a-technical-deep-dive-da81ab27e99f)  
10. Complete Analysis of the React2Shell (CVE-2025-55182) Vulnerability | Enki White Hat, accessed December 22, 2025, [https://www.enki.co.kr/en/media-center/blog/complete-analysis-of-the-react2shell-cve-2025-55182-vulnerability](https://www.enki.co.kr/en/media-center/blog/complete-analysis-of-the-react2shell-cve-2025-55182-vulnerability)  
11. CVE-2025-55182: React2Shell Critical Vulnerability — what it is and what to do \- Dynatrace, accessed December 22, 2025, [https://www.dynatrace.com/news/blog/cve-2025-55182-react2shell-critical-vulnerability-what-it-is-and-what-to-do/](https://www.dynatrace.com/news/blog/cve-2025-55182-react2shell-critical-vulnerability-what-it-is-and-what-to-do/)  
12. PeerBlight Linux Backdoor Exploits React2Shell CVE-2025-55182 | Huntress, accessed December 22, 2025, [https://www.huntress.com/blog/peerblight-linux-backdoor-exploits-react2shell](https://www.huntress.com/blog/peerblight-linux-backdoor-exploits-react2shell)  
13. AI Slop NextJS RCE Write UP \- GitHub Gist, accessed December 22, 2025, [https://gist.github.com/HerringtonDarkholme/87f14efca45f7d38740be9f53849a89f](https://gist.github.com/HerringtonDarkholme/87f14efca45f7d38740be9f53849a89f)  
14. The deepest research on the React Meltdown (CVE-2025-55182 ..., accessed December 22, 2025, [https://raven.io/blog/the-deepest-research-on-the-react-meltdown-cve-2025-55182-and-why-your-waf-rule-patch-leaves-you-exposed](https://raven.io/blog/the-deepest-research-on-the-react-meltdown-cve-2025-55182-and-why-your-waf-rule-patch-leaves-you-exposed)  
15. CVE-2025-55182: React2Shell Analysis, Proof-of-Concept Chaos, and In-the-Wild Exploitation \- Trend Micro, accessed December 22, 2025, [https://www.trendmicro.com/it\_it/research/25/l/CVE-2025-55182-analysis-poc-itw.html](https://www.trendmicro.com/it_it/research/25/l/CVE-2025-55182-analysis-poc-itw.html)  
16. React's CVE-2025-55182 Is Now Actively Exploitable: Verified PoC ..., accessed December 22, 2025, [https://www.ox.security/blog/reacts-cve-2025-55182-is-now-actively-exploitable-verified-poc/](https://www.ox.security/blog/reacts-cve-2025-55182-is-now-actively-exploitable-verified-poc/)  
17. CVE-2025-55182: React Server Components are Vulnerable to RCE \- Miggo Security, accessed December 22, 2025, [https://www.miggo.io/vulnerability-database/cve/CVE-2025-55182](https://www.miggo.io/vulnerability-database/cve/CVE-2025-55182)  
18. assetnote/react2shell-scanner: High Fidelity Detection Mechanism for RSC/Next.js RCE (CVE-2025-55182 & CVE-2025-66478) \- GitHub, accessed December 22, 2025, [https://github.com/assetnote/react2shell-scanner](https://github.com/assetnote/react2shell-scanner)  
19. Critical vulnerability in React and Next.js (CVE-2025-55182) | Blog ..., accessed December 22, 2025, [https://www.vulncheck.com/blog/cve-2025-55182-react-nextjs](https://www.vulncheck.com/blog/cve-2025-55182-react-nextjs)  
20. And then, and then, and then … give me the (react2)shell | by Jang \- Medium, accessed December 22, 2025, [https://testbnull.medium.com/and-then-and-then-and-then-give-me-the-react2-shell-3c4b60ebaef9](https://testbnull.medium.com/and-then-and-then-and-then-give-me-the-react2-shell-3c4b60ebaef9)  
21. React2Shell | Going Granular: A Deep-Deep-Deep Technical Analysis of CVE-2025-55182, accessed December 22, 2025, [https://www.ox.security/blog/react2shell-going-granular-a-deep-deep-deep-technical-analysis-of-cve-2025-55182/](https://www.ox.security/blog/react2shell-going-granular-a-deep-deep-deep-technical-analysis-of-cve-2025-55182/)  
22. CVE-2025-55182: Critical Vulnerability, React2Shell, Allows for Unauthenticated RCE, accessed December 22, 2025, [https://www.cybereason.com/blog/cve-2025-55182-rce-vulnerability](https://www.cybereason.com/blog/cve-2025-55182-rce-vulnerability)  
23. Exploitation of Critical Vulnerability in React Server Components (Updated December 12), accessed December 22, 2025, [https://unit42.paloaltonetworks.com/cve-2025-55182-react-and-cve-2025-66478-next/](https://unit42.paloaltonetworks.com/cve-2025-55182-react-and-cve-2025-66478-next/)  
24. Critical React & Next.js RCE Vulnerability CVE-2025-55182 Fix Guide \- Aikido, accessed December 22, 2025, [https://www.aikido.dev/blog/react-nextjs-cve-2025-55182-rce](https://www.aikido.dev/blog/react-nextjs-cve-2025-55182-rce)  
25. React and Next.js Vulnerable to Critical (10.0) Remote Code Execution | CyberAlberta, accessed December 22, 2025, [https://cyberalberta.ca/react-and-nextjs-vulnerable-to-critical-100-remote-code-execution](https://cyberalberta.ca/react-and-nextjs-vulnerable-to-critical-100-remote-code-execution)  
26. React/Next.js Remote Code Execution Vulnerability (CVE-2025-55182/CVE-2025-66478) Notice \- NSFOCUS, Inc., a global network and cyber security leader, protects enterprises and carriers from advanced cyber attacks., accessed December 22, 2025, [https://nsfocusglobal.com/react-next-js-remote-code-execution-vulnerability-cve-2025-55182-cve-2025-66478-notice/](https://nsfocusglobal.com/react-next-js-remote-code-execution-vulnerability-cve-2025-55182-cve-2025-66478-notice/)  
27. China-nexus cyber threat groups rapidly exploit React2Shell vulnerability (CVE-2025-55182) | AWS Security Blog, accessed December 22, 2025, [https://aws.amazon.com/blogs/security/china-nexus-cyber-threat-groups-rapidly-exploit-react2shell-vulnerability-cve-2025-55182/](https://aws.amazon.com/blogs/security/china-nexus-cyber-threat-groups-rapidly-exploit-react2shell-vulnerability-cve-2025-55182/)  
28. React2Shell (CVE-2025-55182) \- Critical (CSVV 10.0) Unauthenticated RCE in React ecosystem : r/cybersecurity \- Reddit, accessed December 22, 2025, [https://www.reddit.com/r/cybersecurity/comments/1pe829q/react2shell\_cve202555182\_critical\_csvv\_100/](https://www.reddit.com/r/cybersecurity/comments/1pe829q/react2shell_cve202555182_critical_csvv_100/)  
29. Chinese hackers rapidly exploit critical React2Shell flaw \- CyberInsider, accessed December 22, 2025, [https://cyberinsider.com/chinese-hackers-rapidly-exploit-critical-react2shell-flaw/](https://cyberinsider.com/chinese-hackers-rapidly-exploit-critical-react2shell-flaw/)  
30. React2Shell: A Critical Vulnerability With Global Impact – What Organizations Should Know, accessed December 22, 2025, [https://www.cegeka.com/en/blogs/react2shell-critical-vulnerability](https://www.cegeka.com/en/blogs/react2shell-critical-vulnerability)  
31. CVE-2025-55182—The React2Shell vulnerability you need to patch right now, accessed December 22, 2025, [https://www.hackthebox.com/blog/react2shell-cve-2025-55182-threat-spotlight](https://www.hackthebox.com/blog/react2shell-cve-2025-55182-threat-spotlight)  
32. Responding to React2Shell | Critical Vulnerability \- PacketWatch, accessed December 22, 2025, [https://packetwatch.com/resources/blog/responding-to-react2shell](https://packetwatch.com/resources/blog/responding-to-react2shell)  
33. React2Shell: What To Know About The Critical React RCE Vulnerability \- StackHawk, accessed December 22, 2025, [https://www.stackhawk.com/blog/react2shell-vulnerability-response/](https://www.stackhawk.com/blog/react2shell-vulnerability-response/)  
34. FINRA Cybersecurity Alert – React2Shell, accessed December 22, 2025, [https://www.finra.org/guidance/guidance/cybersecurity-advisory-react2shell](https://www.finra.org/guidance/guidance/cybersecurity-advisory-react2shell)