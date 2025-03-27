"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { AlertCircle, FileText, Image, Loader2, Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"

type Message = {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
  isError?: boolean
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your AI technical support assistant. How can I help you today?",
      role: "assistant",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null)

  const documents = [
    {
      id: "1",
      name: "Technical Manual v2.3.pdf",
      size: "4.2 MB",
      date: "2 days ago",
    },
    {
      id: "2",
      name: "Field Guide 2025.pdf",
      size: "2.8 MB",
      date: "1 week ago",
    },
    {
      id: "3",
      name: "Equipment Specs.pdf",
      size: "8.5 MB",
      date: "2 weeks ago",
    },
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      let aiResponse: Message

      // Check if the query is off-topic
      if (
        !input.toLowerCase().includes("manual") &&
        !input.toLowerCase().includes("equipment") &&
        !input.toLowerCase().includes("technical") &&
        !input.toLowerCase().includes("guide") &&
        !input.toLowerCase().includes("error") &&
        !input.toLowerCase().includes("sensor") &&
        !input.toLowerCase().includes("calibrate") &&
        !input.toLowerCase().includes("maintenance")
      ) {
        // Off-topic query
        aiResponse = {
          id: (Date.now() + 1).toString(),
          content:
            "I can only answer technical questions from the uploaded manuals. Please ask a question related to your technical documentation.",
          role: "assistant",
          timestamp: new Date(),
          isError: true,
        }
      } else {
        // On-topic query
        const responses = [
          "According to the technical manual, you should calibrate the sensor by following these steps: 1) Power off the device, 2) Press and hold the reset button for 5 seconds, 3) Power on while still holding the button, 4) Release when the LED flashes green.",
          "The maintenance schedule in the field guide recommends servicing the equipment every 3 months under normal conditions, or monthly in high-dust environments.",
          "Error code E-45 indicates a power supply issue. Check the input voltage and ensure it's within the specified range of 110-240V. If the voltage is correct, the internal power module may need replacement.",
          "The technical specifications indicate that the Model X-200 requires a 24V DC power supply with at least 2.5A current capacity. Always use the manufacturer-approved power adapter.",
        ]

        const randomResponse = responses[Math.floor(Math.random() * responses.length)]

        aiResponse = {
          id: (Date.now() + 1).toString(),
          content: randomResponse,
          role: "assistant",
          timestamp: new Date(),
        }
      }

      setMessages((prev) => [...prev, aiResponse])
      setIsLoading(false)
    }, 1500)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col md:flex-row md:gap-4">
      <div className="hidden md:flex md:w-64 md:flex-col md:gap-4">
        <Card>
          <CardHeader className="py-4">
            <CardTitle className="text-sm font-medium">Documents</CardTitle>
            <CardDescription className="text-xs">Your uploaded technical manuals</CardDescription>
          </CardHeader>
          <CardContent className="px-2 py-0">
            <div className="space-y-1">
              {documents.map((doc) => (
                <Button
                  key={doc.id}
                  variant={selectedDocument === doc.id ? "secondary" : "ghost"}
                  className="w-full justify-start text-left"
                  onClick={() => setSelectedDocument(doc.id)}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  <span className="truncate">{doc.name}</span>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="py-4">
            <CardTitle className="text-sm font-medium">Subscription</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Free tier</span>
                <span className="text-sm font-medium">28/50</span>
              </div>
              <div className="h-2 w-full rounded-full bg-muted">
                <div className="h-full rounded-full bg-primary" style={{ width: "56%" }} />
              </div>
              <p className="text-xs text-muted-foreground">56% of monthly query quota used</p>
              <Button variant="outline" size="sm" className="mt-2 w-full">
                Upgrade to Pro
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
      <div className="flex flex-1 flex-col rounded-lg border bg-background">
        <Tabs defaultValue="chat" className="flex flex-1 flex-col">
          <div className="border-b px-4">
            <TabsList className="h-12">
              <TabsTrigger value="chat" className="data-[state=active]:bg-background">
                Chat
              </TabsTrigger>
              <TabsTrigger value="documents" className="md:hidden data-[state=active]:bg-background">
                Documents
              </TabsTrigger>
            </TabsList>
          </div>
          <TabsContent value="chat" className="flex-1 p-0 data-[state=active]:flex data-[state=active]:flex-col">
            <ScrollArea className="flex-1 p-4">
              <div className="space-y-4 pb-4">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`flex max-w-[80%] gap-3 rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : message.isError
                            ? "border-red-200 bg-red-50 text-red-900 dark:bg-red-900/10 dark:text-red-400"
                            : "bg-muted"
                      }`}
                    >
                      {message.role === "assistant" && (
                        <Avatar className="h-8 w-8">
                          <AvatarImage src="/placeholder.svg?height=32&width=32" alt="AI" />
                          <AvatarFallback>AI</AvatarFallback>
                        </Avatar>
                      )}
                      <div className="flex flex-col gap-1">
                        <div className="text-sm">{message.content}</div>
                        <div className="text-xs opacity-60">
                          {message.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="flex max-w-[80%] gap-3 rounded-lg bg-muted p-4">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src="/placeholder.svg?height=32&width=32" alt="AI" />
                        <AvatarFallback>AI</AvatarFallback>
                      </Avatar>
                      <div className="flex items-center">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </ScrollArea>
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Button variant="outline" size="icon" className="shrink-0">
                  <Image className="h-4 w-4" />
                  <span className="sr-only">Attach screenshot</span>
                </Button>
                <div className="relative flex-1">
                  <Input
                    placeholder="Ask a question about your technical documentation..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    className="pr-12"
                  />
                  <Button
                    size="icon"
                    className="absolute right-1 top-1 h-7 w-7"
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                  >
                    <Send className="h-4 w-4" />
                    <span className="sr-only">Send</span>
                  </Button>
                </div>
              </div>
              <Alert className="mt-4 bg-muted/50">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>AI Technical Support</AlertTitle>
                <AlertDescription>
                  I can only answer questions about your uploaded technical documentation. For other inquiries, please
                  contact customer support.
                </AlertDescription>
              </Alert>
            </div>
          </TabsContent>
          <TabsContent value="documents" className="p-4 md:hidden">
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Your Documents</h3>
              <div className="space-y-2">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className={`flex items-center gap-3 rounded-lg border p-3 ${
                      selectedDocument === doc.id ? "border-primary bg-primary/5" : ""
                    }`}
                    onClick={() => setSelectedDocument(doc.id)}
                  >
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-medium">{doc.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {doc.size} • Uploaded {doc.date}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="space-y-2">
                <h3 className="text-lg font-medium">Subscription</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Free tier</span>
                    <span className="text-sm font-medium">28/50</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-muted">
                    <div className="h-full rounded-full bg-primary" style={{ width: "56%" }} />
                  </div>
                  <p className="text-xs text-muted-foreground">56% of monthly query quota used</p>
                  <Button variant="outline" size="sm" className="mt-2 w-full">
                    Upgrade to Pro
                  </Button>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

